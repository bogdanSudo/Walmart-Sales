import math
import seaborn as sns
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
    df['Month'] = df['Date'].dt.month
    df['Week'] = df['Date'].dt.isocalendar().week  # Numărul săptămânii în an (1-52)
    # media vanzarilor reale saptamanel
    yearly_result = df.groupby('Year')[['Real_Weekly_Sales', 'Weekly_Sales']].agg(['mean']).reset_index()

    yearly_result.columns = ['Year', 'Real_avg_weekly_sales', 'Nominal_Weekly_Sales']
    # delta reprezinta diferenta procentuala cauzata de inflatie
    yearly_result['Delta'] = ((yearly_result['Nominal_Weekly_Sales'] - yearly_result['Real_avg_weekly_sales'])
                              / yearly_result['Nominal_Weekly_Sales']) * 100
    return yearly_result

def monthly_sales(df):
    monthly_res = df.groupby('Month')[['Real_Weekly_Sales']].agg(['mean']).reset_index()
    monthly_res.columns = ['Month', 'Real_avg_weekly_sales']

    plt.figure(figsize=(10, 5))
    sns.lineplot(data=monthly_res, x='Month', y='Real_avg_weekly_sales', marker='o', color='red')
    plt.title('Media vanzari pe luni')
    plt.xticks(range(1, 13))
    plt.grid(True)
    plt.show()
    return monthly_res

def graph_yearly_sales(df):
    yearly_result = df.groupby('Year')[['Real_Weekly_Sales']].agg(['mean']).reset_index()

    yearly_result.columns = ['Year', 'Year_sales']
    plt.figure(figsize=(10, 5))
    sns.lineplot(data=yearly_result, x='Year', y='Year_sales', marker='o', color='red')
    plt.xticks(yearly_result['Year'].unique())
    plt.title('Media vanzari pe ani')
    plt.grid(True)
    plt.show()
    print(yearly_result)

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

#criteriu pentru valorile reale ale vanzarilor saptamanale
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

def remove_lower_avg(df):
    avg_weekly_real_value = df["Real_Weekly_Sales"].mean()
    df = df[df['Real_Weekly_Sales'] > avg_weekly_real_value]
    return df

def perform_analysis_store(df):
    stats_store = df.groupby('Store').agg({
                            'Weekly_Sales': ['mean','min', 'max'],
                            'Fuel_Price': 'mean',
                            'Unemployment': ['mean','min', 'max']
    })
    stats_store.columns = ['_'.join(col).strip()
                                     for col in stats_store.columns.values]
    pd.options.display.float_format = '{:.2f}'.format
    print("Statistici per magazin\n", stats_store)


def mean_non_holiday_real_sales(df):
    pivot_sales = df.pivot_table(
        values = 'Real_Weekly_Sales',
        index = 'Store',
        columns = 'Holiday_Flag',
        aggfunc = 'mean',
        fill_value = 0
    ).round(2)
    pivot_sales.columns = ['Vanzari normale', 'Vanzari sarbatoare']
    print('tabel pivot :sapt normala vs sarbatoare\n',
          pivot_sales)

def unemployment_sales(df):
    df_unemployment = df.copy()
    df_unemployment['Unemployment_Status'] = pd.cut(
        df['Unemployment'],
        bins = [0,5,8,12],
        labels = ['Low', 'Medium', 'High']
    )
    pivot_unemployment_real_sales = df_unemployment.pivot_table(
                                    values = 'Real_Weekly_Sales',
                                    index = 'Unemployment_Status',
                                    columns = 'Holiday_Flag',
                                    aggfunc = 'mean'
                                    )
    pivot_unemployment_real_sales.columns = ['Vanzari normale', 'Vanzari sarbatoare']
    print(pivot_unemployment_real_sales)

def fuel_price_real_sales(df):
    fuel = df.copy()
    fuel['Fuel_Status'] = pd.qcut(
        fuel['Fuel_Price'],
        q = 2, #impart dupa mediana
        labels = ['Ieftin', 'Scump']
    )
    pivot_fuel = fuel.pivot_table(
                    values = 'Real_Weekly_Sales',
                    index = 'Store',
                    columns = 'Fuel_Status',
                    aggfunc = 'mean',
                    fill_value= 0 #pun 0 daca am NA
    )
    print('Vanzari per magazin in functie de situatia pretulului combustibilului\n',
          pivot_fuel)


def hist_numeric_var(df):
    numerical_cols = df.select_dtypes(include = 'number').columns
    numerical_cols
    n_cols = 3
    n_rows = math.ceil(len(numerical_cols)/n_cols)
    plt.figure(figsize = (6*n_cols, 4*n_rows))
    for i, col in enumerate(numerical_cols):
        plt.subplot(n_rows, n_cols, i + 1)  # Creăm un subplot în grila de n_rows x n_cols; i+1 pentru indexarea subgraficelor începând de la 1
        plt.hist(df[col].dropna(), bins=30, edgecolor='black', color='skyblue')  # Construim histograma pentru coloana curentă, eliminând valorile lipsă
        plt.title(f'Distribuția: {col}')  # Setăm titlul graficului cu numele coloanei
        plt.xlabel(col)  # Etichetă pentru axa x, indicând numele variabilei
        plt.ylabel('Frecvență')  # Etichetă pentru axa y, indicând frecvența valorilor
    plt.tight_layout()  # Ajustăm automat spațiile dintre subgrafice pentru a evita suprapunerea
    plt.show()


#analiza corelatiilor intre variabile
def corr_analysis(df):
    corr_matrix = df.corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title("Matricea de corelație pentru variabilele numerice")
    plt.tight_layout()
    plt.show()

def plot_top_10_stores(df):
    # 1. Grupăm după Store și calculăm media vânzărilor REALE (Real_Weekly_Sales)
    store_sales = df.groupby('Store')['Real_Weekly_Sales'].mean()

    # 2. Selectăm cele mai mari 10 valori
    top_10 = store_sales.sort_values(ascending=False).head(10)

    # 3. Creăm figura
    plt.figure(figsize=(12, 6))

    # 4. Construim barplot-ul folosind plt.bar (varianta basic)
    # Convertim indexul (Codurile Store) în string ca să nu le pună pe o axă numerică ciudată
    plt.bar(top_10.index.astype(str), top_10.values, color='green', edgecolor='black')

    # 5. Personalizare (Titlu, Etichete)
    plt.title("Top 10 magazine dupa vanzarile medii reale", fontsize=14)
    plt.xlabel("Store ID", fontsize=12)
    plt.ylabel("Vânzări Medii Reale (USD)", fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7) # Adăugăm linii de ghidaj pe orizontală

    # 6. Adăugăm valorile deasupra barelor (opțional, pentru claritate)
    for i, val in enumerate(top_10.values):
        plt.text(i, val, f'{val:,.0f}', ha='center', va='bottom', fontsize=10)

    plt.show()
#boxplot pt vanzari reale in functie de vacanta
