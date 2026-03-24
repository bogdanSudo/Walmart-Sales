import kagglehub
import pandas as pd
import seaborn as sns
from pandas import Series
import data_functions as process_data
from data_functions import convert_to_celsius, average_weekly_sales, map_store_sales, avg_store_sales, \
    add_real_sales_column, group_yearly_sales, comp_warm_cold_weeks, avg_holiday_sales, avg_no_holiday_sales, \
    graphic_sales, get_regr_model, remove_outliers, remove_lower_avg, perform_analysis_store, \
    mean_non_holiday_real_sales, unemployment_sales, fuel_price_real_sales, hist_numeric_var, corr_analysis, \
    monthly_sales, graph_yearly_sales, plot_top_10_stores, plot_holiday_sales_change, plot_temp_change

PATH = "/Users/bogdan/Desktop/an3.sem2/PacheteSoftware/proiect"
NUME_FISIER_DATE = "Walmart.csv"
# Download latest version
#path = kagglehub.dataset_download("yasserh/walmart-dataset")
#print("Path to dataset files:", path)
#Path to dataset files: /Users/bogdan/.cache/kagglehub/datasets/yasserh/walmart-dataset/versions/1

#analiza activităţii organizaţiei şi
#a eventualelor posibilităţi de extindere a acesteia.
def main():
    df = pd.read_csv(NUME_FISIER_DATE)
    pd.set_option('display.max_columns', None)


    df = df.dropna(subset = 'Weekly_Sales')

    df['Temperature_C'] = df['Temperature'].apply(convert_to_celsius)

    list_weekly_sales = df["Weekly_Sales"].tolist()
    #nu tin cont de care market este, le calculez ca o medie globala
    print("vanzarea medie globala saptamanala este = ",average_weekly_sales(list_weekly_sales), "$")

    #dictionar: grupez vanzarile saptamanale dupa fiecare magazin
    list_stores = df["Store"].tolist()

    #dict_store_sales contine vanzarile saptamanale grupate pe magazine
    dict_store_sales = map_store_sales(list_weekly_sales, list_stores)

    # magazin mapat cu vanzarile medii saptamanale
    dict_avg_store_sales, max_avg_sales, max_avg_sales_store = avg_store_sales(dict_store_sales)

    print("Magazinul cu vanzarile medii saptamanel cele mai mari este store", max_avg_sales_store,
           "cu vanzarii medii de ", max_avg_sales, "$")

    #analiza vanzarilor reale, ajustate folosindu-ne de consumer price index
    df = add_real_sales_column(df)
    print("media vanzarilor nominale per magazine global = ", average_weekly_sales(df['Weekly_Sales']), "$")
    print("media vanzarilor real per magazine global = ", average_weekly_sales(df['Real_Weekly_Sales']),"$")

    #vreau sa grupez vanzarile reale pe ani sau si per ani si per magazin
    yearly_result = group_yearly_sales(df)
    # diferenta este mai mare de la an la an, fapt ceea ce indica ca Walmart ar trebui sa aiba grija la marja de profit
    print(yearly_result)

#TESTARE loc si iloc de la seminar
#idee pt loc: sa compar vanzarile in sapt calduroase cu sapt friguroase (temperaturi > 15 grade celsius si mai mici de <15)

    nr_warm_weeks, nr_cold_weeks, dif_proc = comp_warm_cold_weeks(df)
    print("nr de saptam calduroase =", nr_warm_weeks,
          "\nnr de sapt friguroase =", nr_cold_weeks,
          "\ndif procentuala =", dif_proc,"%")

    #se poate observa ca in perioada vacantelor vanzarile cresc semnificativ
    print("vanzarii medii in vacanta= ", avg_holiday_sales(df), "$")
    print("vanzarii medii cand nu e vacanta= ", avg_no_holiday_sales(df), "$")

    get_regr_model(df)
    #R^2 = 0.211
    # p_value al modelului << 0.05 => modelul e semnfiicativ statistic
    #p_value(Temperature) >> 0.05 = > temperatura nu influenteaza vanzarile
    #restul variabilelor influenteaza semnificativ vanzarile
    graphic_sales(df)
    #din grafic ne putem da seama ca seria de timp nu are trend, dar are sezonalitate
    #vanzarile reale sunt mai mici decat vanzarile nominale
    #vanzarile cresc in fiecare an in noiembrie,decembrie
    #datoria zilei recunostintei si a sarbatorilor de craciun
    #pt ca reziduurile sa nu fie corelate trebuie ca DW = 2


    #stergea de coloane / inregistrari: incerc sa scot randuri care nu indeplinesc o anumita conditie
    print("minimul este=", df['Real_Weekly_Sales'].min())
    df = remove_lower_avg(df)
    print("minimul este=",df['Real_Weekly_Sales'].min())

    #sa elimin outlier ?
    print("max cu outlieri este=",df['Real_Weekly_Sales'].max())
    df = remove_outliers(df)
    print("max fara outlieri este=",df['Real_Weekly_Sales'].max())

    perform_analysis_store(df)
    mean_non_holiday_real_sales(df)

    print('Impactul ratei somajului asupra vanzarilor')
    unemployment_sales(df)

    df.drop(['Weekly_Sales'], axis=1, inplace=True)
    fuel_price_real_sales(df)
    hist_numeric_var(df)
    corr_analysis(df)
    monthly_sales(df) #se observa cum cresc vanzarile in noiembrie decembrie (Sarbatori)
    graph_yearly_sales(df)
    plot_top_10_stores(df)

    plot_holiday_sales_change(df)
    #se observa ca in perioada sarbatorilor vanzarile cresc semnificativ
    #mediana are o valoare mai mare, iar potentialul maxim de vanzari difera semnificativ

    plot_temp_change(df)

if __name__ == "__main__":
    main()