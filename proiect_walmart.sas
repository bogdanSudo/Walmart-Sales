proc import datafile = '/home/u64489966/Walmart.csv'
	out = WORK.walmart
	DBMS = CSV
	REPLACE;
	GETNAMES = YES;
run;

proc print data = WORK.walmart (OBS=10);
	title 'Primele 10 observatii din setul de date';
run;

*modific formatele pt holiday_flag si pt somaj;
proc format;
	VALUE tip_saptamana
	0 = 'Saptamana-Lucratoare'
	1 = 'Vacanta';
	
	VALUE nivel_somaj
	LOW - 6 = 'Scazut (sub 6%)'
	6 - 8 = 'Mediu (6-8%)'
	8 - HIGH = 'Ridicat(peste 8%)';
run;


DATA WORK.walmart_fmt;
	SET WORK.walmart;
	LABEL Weekly_Sales = 'Vanzari saptamanle ($)'
		  Holiday_Flag = 'Tip Saptamana'
		  Unemployment = 'Nivel Somaj';
	format Holiday_Flag tip_saptamana.
		   Unemployment nivel_somaj.;
run;

proc print data = WORK.walmart_fmt (OBS=10) noobs label;
	title 'Raport Walmart cu formate noi';
	VAR Store Date Weekly_Sales Holiday_Flag Unemployment;
	
run;

*procesarea datelor in functie de criterii;
*convertez temperatura in grade Celsius;

DATA WORK.walmart_complet;
	SET WORK.walmart;
	temp_C = round((Temperature-32)*5/9 , 0.1);
	an = year(Date);
	luna = month(Date);
	
	*impart pe cateogrii vanzarile;
	if Weekly_Sales < 500000 then categ_firma = 'mici';
	else if Weekly_Sales <1500000 then categ_firma = 'medii';
	else if Weekly_Sales < 2500000 then categ_firma = 'mari';
	else categ_firma = 'foarte mari';
	
	label temp_C = 'Temperatura (Celsius)'
		  categ_firma = 'Categorie vanzari';
run;		  
	
proc print data = WORK.walmart_complet (OBS=10) NOOBS;
	title 'set de date Walmart cu variabile pe categorii';
	var Store Date Weekly_Sales categ_firma temp_C an luna;
run;

*subseturi din datele initiale;
*iau prima data subset saptamanile cu sarbatoare;
DATA WORK.sarbatori;
	set WORK.walmart_complet;
	where Holiday_Flag = 1;
run;

*iau magazinele cu index intre 1 si 10;
DATA WORK.magazine110;
	set WORK.walmart_complet;
	if Store <= 10;
run;

*saptamani cu vanzari mai mari de 2mil. $;
DATA WORK.vanzari_mari;
	set WORK.walmart_complet;
	where Weekly_Sales > 2000000;
run;

proc print data = WORK.sarbatori (OBS=5) NOOBS;
	title 'Saptamani de sarbatoare';
	VAR Store Date Weekly_Sales Holiday_Flag;
run;

proc print data = WORK.magazine110 (OBS = 5) NOOBS;
	title 'Magazine cu ID intre 1 si 10';
	VAR Store Weekly_Sales;
run;

*statistici pt saptamanile cu vanzari mari;
proc means data = WORK.sarbatori N MEAN MIN MAX;
	title 'Statistici vanzari in perioada sarbatorilor';
	VAR Weekly_Sales;
run;

*rapoarte agregate;
*ce procent de saptamani sunt cu sarbatoare si fara;
*media vanzarilor pt fiecare magazin;
proc freq data = WORK.walmart_complet;
	tables Holiday_Flag/ NOCUM;
	format Holiday_Flag tip_saptamana;
	title 'Distributia saptamanilor dupa tip';
run;

*vanzarii medii pe categorie;
proc freq data = WORK.walmart_complet;
	tables categ_firma / NOCUM NOPERCENT;
	title 'Nr. saptamani pe categorie de vanzari';
run;

proc sort data = WORK.walmart_complet;
	by Store;
run;

proc means data = WORK.walmart_complet N MEAN MIN MAX SUM;
	by Store;
	VAR Weekly_Sales;
	title 'Statistici per magazin a vanzarilor';
run;

*total pe saptamana ;
proc sort data = WORK.walmart_complet;
	by Holiday_Flag;
run;

proc means data = WORK.walmart_complet SUM;
	CLASS Holiday_Flag;
	var Weekly_Sales;
	format Holiday_Flag tip_saptamana;
	title 'Total vanzari in functie de tipul saptamanii';
run;

* regresie simpla;
* Weekly_SAles = a + b*Unemployment;
proc corr data = WORK.walmart_complet;
	VAR Unemployment Fuel_Price CPI temp_C;
	WITH Weekly_Sales;
	title 'Corelatie vanzari - variabile macroecon';
run;
*coef esste de -0.106, valoare slab ,dar semnificativa
*somajul are cea mai puternica legatura cu vanzarile;
*cand somajul creste, vanzarile scad usor;

proc reg data = WORK.walmart_complet;
	model Weekly_Sales = Unemployment;
	title 'Regresie vanzari in func de somaj';
run;
QUIT;

*grafice;
proc gchart data = WORK.walmart_complet;
	VBAR categ_firma;
	title 'Distributia saptamanilor pe categorie de vanzari';
run;
quit;

proc gchart data = WORK.walmart_complet;
	PIE Holiday_Flag;
	format Holiday_Flag tip_saptamana;
	title 'Proportia saptamanilor libere vs la munca';
run;
quit;
