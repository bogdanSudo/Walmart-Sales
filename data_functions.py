import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf

#functie pentru conversie Farehnheit la Celsius
WARM_TEMPERATURE_C = 15

def convert_to_celsius(fahrenheit):
    return round(((fahrenheit - 32) / 1.8),2)

def average_weekly_sales(sales_list):
    sales_sum = sum(sales_list)
    nr_weeks = len(sales_list)
    return round(sales_sum/nr_weeks, 2)

#fiecare cod de magazin are asociata o lista de vanzari saptamanale
def map_store_sales(sales_list, list_stores):
    dict_store_sales = {}
    for i in range(len(list_stores)):
        store = list_stores[i]
        sale = sales_list[i]
        if store not in dict_store_sales:
            dict_store_sales[store] = [sale]
        else:
            dict_store_sales[store].append(sale)

    return dict_store_sales

# calcul media vanzarilor per magazin
def avg_store_sales(dict_store_sales):
    max_avg_sales = 0
    max_avg_sales_store = -1
    dict_avg_store_sales = {}
    for store, weekly_store_sales in dict_store_sales.items():
        avg_weekly_store_sales = round(sum(weekly_store_sales) / len(weekly_store_sales), 2)
        dict_avg_store_sales[store] = avg_weekly_store_sales
        if avg_weekly_store_sales > max_avg_sales:
            max_avg_sales = avg_weekly_store_sales
            max_avg_sales_store = store
    return dict_avg_store_sales, max_avg_sales, max_avg_sales_store

def add_real_sales_column(df):
    df['Real_Weekly_Sales'] = round((df['Weekly_Sales'] / df['CPI']) * 100, 2)
    return df


#df sub forma: an -vanzari_reale - vanzari_nominale - Delta
def group_yearly_sales(df):
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    df['Year'] = df['Date'].dt.year

    # media vanzarilor reale saptamanel
    yearly_result = df.groupby('Year')[['Real_Weekly_Sales', 'Weekly_Sales']].agg(['mean']).reset_index()

    yearly_result.columns = ['Year', 'Real_avg_weekly_sales', 'Nominal_Weekly_Sales']
    # delta reprezinta diferenta procentuala cauzata de inflatie
    yearly_result['Delta'] = ((yearly_result['Nominal_Weekly_Sales'] - yearly_result['Real_avg_weekly_sales'])
                              / yearly_result['Nominal_Weekly_Sales']) * 100
    return yearly_result

def comp_warm_cold_weeks(df):
    warm_weeks = df.loc[(df.Temperature >= WARM_TEMPERATURE_C), 'Real_Weekly_Sales']
    cold_weeks = df.loc[(df.Temperature < WARM_TEMPERATURE_C), 'Real_Weekly_Sales']
    avg_warm = round(warm_weeks.mean(),2)
    avg_cold = round(cold_weeks.mean(), 2)
    nr_warm = len(warm_weeks)
    nr_cold = len(cold_weeks)
    dif_proc = round(((avg_warm - avg_cold) / avg_cold) * 100,2)

    return nr_warm, nr_cold, dif_proc

#calcul valoare medie a vanzarilor in care era si vacanta in valori reale
def avg_holiday_sales(df):
    holiday_weeks = df.loc[df.Holiday_Flag == 1, 'Real_Weekly_Sales']
    return round(holiday_weeks.mean(),2)

def avg_no_holiday_sales(df):
    holiday_weeks = df.loc[df.Holiday_Flag == 0, 'Real_Weekly_Sales']
    return round(holiday_weeks.mean(), 2)

def graphic_sales(df):
    #grupez vanzarile saptamanle (toate magazinele ,indiferent de cod le adun ca sa am vanzarile totale pe saptamana)
    df_weekly_sales = df.groupby('Date')[['Weekly_Sales', 'Real_Weekly_Sales']].mean().reset_index()
    #creez graficul
    plt.figure(figsize = (10,10))
    plt.plot(df_weekly_sales['Date'], df_weekly_sales['Weekly_Sales'],
             label = 'Vanzari nominale', color = 'green', linestyle = '-', linewidth = 1.5)
    plt.plot(df_weekly_sales['Date'], df_weekly_sales['Real_Weekly_Sales'],
             label = 'Vanzari reale', color = 'red', linewidth = 2 )
    plt.title('Evolutia vanzarilor medii saptamanale globale: Nominal vs Real', fontsize = 10)
    plt.xlabel('An - Luna')
    plt.ylabel('Valoare vanzari')
    plt.legend()
    plt.show()

def get_regr_model(df):
    #regresie, dar nu tin cont de sezonalitate (seria nu are trend)
    df = df.sort_values(by = ['Store','Date'])
    df['Trend'] = range(len(df))
    df['Trend'] = range(len(df))  # Trend liniar
    df['Month'] = df['Date'].dt.month.astype(str)  # Sezonalitate lunară
    df['Sales_Lag1'] = df.groupby('Store')['Real_Weekly_Sales'].shift(1)  # Memoria seriei

    # 3. Curățăm valorile NaN (create de shift)
    df_clean = df.dropna()

    # 4. Noua ecuație (am scos Temperatura pentru că era irelevantă în testul tău anterior)
    regr_ec_nou = 'Real_Weekly_Sales ~ Sales_Lag1 + Trend + C(Month) + Fuel_Price + CPI + Unemployment + Holiday_Flag'

    regr_model = smf.ols(formula=regr_ec_nou, data=df_clean).fit()

    print(regr_model.summary())

def remove_outliers(df):
    Q1 = df['Real_Weekly_Sales'].quantile(q = 0.25)
    Q3 = df['Real_Weekly_Sales'].quantile(q = 0.75)
    IQR = Q3 - Q1
    inf_limit = Q1 - 1.5 * IQR
    sup_limit = Q3 + 1.5 * IQR
    df_remove_outliers = df[(df['Real_Weekly_Sales'] <= sup_limit) &
                            (df['Real_Weekly_Sales'] >= inf_limit)
                            ]
    return df_remove_outliers
