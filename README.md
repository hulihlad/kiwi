# kiwi weekend task - find flight and book ticket



Obsah nápovědy:
1) soubory
2) řešení
3) nápověda spuštení
4) konfigurační hodnoty v souboru conf.py
5) příklady použití



1) soubory:

	conf.py 					- konfigurační soubor
	flight.py 					- program
	iata_airports.dat 			- data s lokacemi dle IATA
	iata_online_airports.dat* 	- data s lokacemi dle IATA stažené z online zdroje
			*soubor je vytvořen jen pokud se stahuje aktuální seznam IATA lokací z internetu.



2) řešení:

	- vytvořím slovník IATA lokací z uloženého souboru nebo z online zdroje (requests, re)
	- získám vstupní data od uživatele z argumentu a získám seznam proměnných k vyhledání letu (optionparser )
	- vygeneruji url s parametry pro vyhledání letu (urlib)
	- na základě dat vrácených o vyhledaném letu vytvořím json pro odeslání dat pro book letenky (json)
	- zavolám book api, odešlu json a získám odpověď
	- pokud opdověď obsahuje potvrzovací kód, vypíšu konfirmační kód jinak nulu




3) nápověda spuštení:


	Usage: flight.py [options]
	
	Options:
	  -h, --help       show this help message and exit
	  --one-way        indikuje potrebu zakaznika letet jenom jednim smerem
	                    (default)
	  --return		   zabookovat let s cestujicim, ktery v destinaci zustava
	                    tento pocet dnu [int]
	  --cheapest       zabookuje nejlevnejsi let (default)
	  --fastest        zabookoje nejrychlejsi let
	  --bags	       zabookovat let se zavazadly s timto poctem zavazadel
	                    [int]
	  --from 	       odlet z letiste IATA code [str]
	  --to             cilova destinace IATA code [str]
	  --date		   date of route [YYYY-MM-DD]




4) konfigurační hodnoty v souboru conf.py:



	flight_search_server_url		- api url for search flights
	book_api_server					- api url for search flights 
	iata_source 					- nastavení zdroje IATA lokací, "local" pro užití lokálního zdroje dat, "online" pro stažení IATA kódu z online zdroje
	iata_source_online_url			- url s IATA kódy v plaintextu
	logging 						- nastavení logování ( nastav 0 pro žádné dodatečné informace nebo nastav 1 pro zobrazení podrobností )
	
	Další nastavení osobních údajů cestujícího:
	psg_title 		=  Mr / Mrs.
	psg_documID 	=  číslo pasu
	psg_email 		=  emailová adresa
	psg_first_name 	=  křestní jméno
	psg_last_name 	=  příjmení
	psg_birthday 	=  datum narození YYYY-MM-DD




5) příklady použití: 



	příklad užití při nastavení logging = 0 (default)
 

		 	./flight.py --from NYC --to PRG --date 2018-03-03
		>>> E353ICA
		
		 	./flight.py --from NYC --to PRG --date 2018-03-03 --return 6  --bags 8
		>>> CQGUU3Q
		
			./flight.py --from NYC --to PRG --date 2018-03-03 --return 6  --bags 8 --fastest
		>>> AGOBZ5Q
		
			./flight.py
		>>> AttributeError: ERROR: Missing reqired argument '--date' 
		
		 	./flight.py --from NYC --to PRG --date 2333-03-03 --return 6  --bags 8 --fastest
		>>> 0


	příklad užití při nastavení logging = 1

		./flight.py --from NYC --to PRG --date 2018-03-03
	>>>	---------------- route parameters ----------------
		From: [NYC - 22 ] : NEW_YORK,_NEW_YORK,_USA
		To:   [PRG - 418 ] : PRAGUE,_CZECH_REPUBLIC
		Date: 2018-03-03
		Searching for cheapest route
		Searching for return ticket in: 0 day/s
		Searching for ticket with 0 bags
		--------------------------------------------------
		Your book reservation ticket code: 
		APYRSNI
		
		
		./flight.py --from NYC --to PRG --date 2018-03-03 --return 6  --bags 8
	>>>	---------------- route parameters ----------------
		From: [NYC - 22 ] : NEW_YORK,_NEW_YORK,_USA
		To:   [PRG - 418 ] : PRAGUE,_CZECH_REPUBLIC
		Date: 2018-03-03
		Searching for cheapest route
		Searching for return ticket in: 6 day/s
		Searching for ticket with 8 bags
		--------------------------------------------------
		Your book reservation ticket code: 
		CNZKLMQ
		
		
		./flight.py --from NYC --to PRG --date 2018-03-03 --return 6  --bags 8 --fastest
	>>>	---------------- route parameters ----------------
		From: [NYC - 22 ] : NEW_YORK,_NEW_YORK,_USA
		To:   [PRG - 418 ] : PRAGUE,_CZECH_REPUBLIC
		Date: 2018-03-03
		Searching for fastest route
		Searching for return ticket in: 6 day/s
		Searching for ticket with 8 bags
		--------------------------------------------------
		Your book reservation ticket code: 
		B4RSPII
		
		
		./flight.py
	>>> AttributeError: ERROR: Missing reqired argument '--date' 
		
		
		
		./flight.py --from NYC --to PRG --date 2333-03-03 --return 6  --bags 8 --fastest
	>>>	---------------- route parameters ----------------
		From: [NYC - 22 ] : NEW_YORK,_NEW_YORK,_USA
		To:   [PRG - 418 ] : PRAGUE,_CZECH_REPUBLIC
		Date: 2333-03-03
		Searching for fastest route
		Searching for return ticket in: 6 day/s
		Searching for ticket with 8 bags
		--------------------------------------------------
		ERR: No flight founded! 
		0
