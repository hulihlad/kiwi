#!/usr/bin/env python

#import lib
import requests
import re
import json
import urllib
from optparse import OptionParser
from datetime import datetime, timedelta

#import modules
from conf import *

# variables
iata_codes_dict = dict()

# functions
def download_actual_iata_codes():
	# download actual IATA codes (this function could be set in conf file)
	if logging == 1:
		print('Downloading actual IATA codes...')
	try:
		response = requests.get(iata_source_online_url)
		iata_online_file = open("iata_online_airports.dat","w")
	 	iata_online_file.write(response.text)
		iata_online_file.close() 
	except Exception as err:
		print("ERROR: Can't download actual IATA codes from url: " + iata_source_online_url )
		print("LOG: " + str(err) )

def import_iata_codes():
	# create dictionary from stored iata codes data
	# dict contains IATA location name, area code and IATA code
	try:
		if iata_source == "local":
			iata_file = open("iata_airports.dat","r")
		elif  iata_source == "online":
			download_actual_iata_codes()
			iata_file = open("iata_online_airports.dat","r")
		else:
			iata_file = "None"
			raise ValueError('Bad value in configuration: iata_source.')
		iata_file.close
	except Exception as err:
		print("LOG: " + str(err) )

	try:
		iata_data_list = (iata_file.read().splitlines())[1:]
		for iata_line in iata_data_list:
			iata_code = iata_line[0:3]
			iata_name = iata_line[5:40]
			iata_area = (iata_line[-3:])
			iata_area = re.sub("[^0-9.]", "", iata_area)
			one_iata_dest_list = [iata_name, iata_area]
			iata_codes_dict[iata_code] = one_iata_dest_list
	except Exception as err:
		print("LOG: " + str(err) )

def get_arguments():
	# get user arguments, normalizace output values
	# this function return list which contains:
	# from_destination, from_destination_area, from_destination_IATA, finish_destination, finish_destination_area, finish_destination_IATA, routedate, cheapest_arg, fastest_arg, return_arg, bags_arg]

	parser = OptionParser()
	parser.add_option("--one-way", 		action="store_false", 												help=" indikuje potrebu zakaznika letet jenom jednim smerem (default)")
	parser.add_option("--return", 		action="store",			type="int", 	dest="returnn",				help=" zabookovat let s cestujicim, ktery v destinaci zustava tento pocet dnu [int]",  )
	parser.add_option("--cheapest",  	action="store_false",					dest="cheapest", 			help=" zabookuje nejlevnejsi let (default)")
	parser.add_option("--fastest", 		action="store_false",					dest="fastest",				help=" zabookoje nejrychlejsi let")
	parser.add_option("--bags",  		action="store", 		type="int", 	dest="bags", 				help=" zabookovat let se zavazadly s timto poctem zavazadel [int]", )
	parser.add_option("--from",  		action="store", 		type="string", 	dest="fromm",				help=" odlet z letiste IATA code [str]", )
	parser.add_option("--to", 			action="store", 		type="string", 	dest="to",					help=" cilova destinace IATA code [str]", )	
	parser.add_option("--date", 		action="store", 		type="string", 	dest="routedate",			help=" date of route [YYYY-MM-DD]", )	

	(options, args) = parser.parse_args()
	return_arg = options.returnn
	cheapest_arg = options.cheapest
	fastest_arg = options.fastest
	bags_arg = options.bags
	from_arg = options.fromm
	to_arg = options.to
	routedate = options.routedate
	if routedate == None:
		raise AttributeError("ERROR: Missing reqired argument '--date' ")
	try:
		routedate = datetime.strptime(routedate, "%Y-%m-%d")
	except:
		raise AttributeError("ERROR: Bad date format, use: YYYY-MM-DD")
	if str(fastest_arg) == "False":
		cheapest_arg = 0
		fastest_arg = 1
	else:
		cheapest_arg = 1
		fastest_arg = 0
	if to_arg == None:
		print("ERROR: Missing reqired argument '--to' ")
		raise AttributeError("ERROR: Missing reqired argument '--to' ")
	if from_arg == None:
		print("ERROR: Missing reqired argument '--to' ")
		raise AttributeError("ERROR: Missing reqired argument '--from' ")
	if (bags_arg != None) and (bags_arg > 0):
		bags_arg = bags_arg
	else:
		bags_arg = 0
	if (return_arg != None) and (return_arg > 0):
		return_arg = return_arg
	else:
		return_arg = 0
	try:
		a = iata_codes_dict[to_arg]
	except:
		raise AttributeError("ERROR: Bad airport IATA code. Code was not found: " + to_arg)
	try:
		a = iata_codes_dict[from_arg]
	except:
		raise AttributeError("ERROR: Bad airport IATA code. Code was not found: " + from_arg)
	from_destination = (iata_codes_dict[from_arg])[0]
	from_destination_area = (iata_codes_dict[from_arg])[1]
	from_destination_IATA = from_arg
	finish_destination = (iata_codes_dict[to_arg])[0]
	finish_destination_area = (iata_codes_dict[to_arg])[1]
	finish_destination_IATA = to_arg
	from_destination = from_destination.strip()
	finish_destination = finish_destination.strip()
	from_destination = from_destination.replace(" ", "_")
	finish_destination = finish_destination.replace(" ", "_")

	#print flight properties if logging is turned on
	if logging == 1:
		print("---------------- route parameters ----------------")
		print("From: [" + from_destination_IATA + " - " + from_destination_area + " ] : " + from_destination)
		print("To:   [" + finish_destination_IATA + " - " + finish_destination_area + " ] : " + finish_destination)
		print('Date: '+ str(routedate.strftime("%Y-%m-%d")) )
		if fastest_arg == 1:
			print('Searching for fastest route')
		else:
			print('Searching for cheapest route')
		if return_arg != None:
			print('Searching for return ticket in: ' + str(return_arg) + " day/s")
		if return_arg != None:
			print('Searching for ticket with ' + str(bags_arg) + " bags")

		print("--------------------------------------------------")

	output_list = [from_destination, from_destination_area, from_destination_IATA, finish_destination, finish_destination_area, finish_destination_IATA, routedate, cheapest_arg, fastest_arg, return_arg, bags_arg]
	return output_list

def compose_url_find_flight_api(arguments_list):
	#compose url for find flight API

	from_destination, from_destination_area, from_destination_IATA, finish_destination, finish_destination_area, finish_destination_IATA, routedate, cheapest_arg, fastest_arg, return_arg, bags_arg = arguments_list
	
	#arguments used in each api call
	flight_args = {
					"v"				: 3, 
					"flyFrom"		: from_destination_IATA, 
					"to"			: finish_destination_IATA, 
					"dateFrom"		: (str(routedate.strftime("%d/%m/%Y"))), 
					"limit"			: 1,
					"passengers"	: 1,
					"adults"		: 1,
					"oneforcity"	: 0,
					"one_per_date"	: 0,
					"flyDaysType"	: "departure",
					"directFlights"	: 0,
					"bags"			: bags_arg

					}
	find_flight_url = (flight_search_server_url + "flights?{}").format(urllib.urlencode(flight_args))

	#arguments used when return arg. is used
	if return_arg > 0:
		route_back_date = routedate + timedelta(days=return_arg)
		route_back_date = (str(route_back_date.strftime("%d/%m/%Y"))), 
		route_back_date = (str(route_back_date[0]))
		flight_args = {
					"typeFlight"		: "round", 
					"returnTo"			: route_back_date,
					"returnFlyDaysType" : "departure"
					}
		find_flight_url = (find_flight_url+"&{}").format(urllib.urlencode(flight_args))

	#arguments used when cheapest arg. is used
	if cheapest_arg == 1:
		flight_args = {
					"sort"		: "price", 
					"asc"		: 1
					}
		find_flight_url = (find_flight_url+"&{}").format(urllib.urlencode(flight_args))

	#arguments used when fastest arg. is used
	if fastest_arg == 1:
		flight_args = {
					"sort"		: "duration", 
					"asc"		: 1
					}
		find_flight_url = (find_flight_url+"&{}").format(urllib.urlencode(flight_args))

	return find_flight_url
 


def compose_arg_json_for_book_api(flight_data_dict, user_arguments_list):
	#compose json used for flight book api call
	passanger_data = [{"title": psg_title , "documentID":psg_documID, "email":psg_email, "firstName":psg_first_name, "lastName": psg_last_name, "birthday": psg_birthday }]
	dict_of_book_api_arguments = {}
	booking_token = ((flight_data_dict["data"])[0])["booking_token"]
	currency = flight_data_dict["currency"]
	bags = user_arguments_list[10]
	dict_of_book_api_arguments["booking_token"]=booking_token
	dict_of_book_api_arguments["currency"]=currency
	dict_of_book_api_arguments["bags"]=bags
	dict_of_book_api_arguments["passengers"]=passanger_data
	json_arguments = json.dumps(dict_of_book_api_arguments)
	json_arguments = json.loads(json_arguments)
	return json_arguments




#get IATA airports data
import_iata_codes()

#get user arguments
user_arguments_list = get_arguments()

# compose url for flight api 
url = compose_url_find_flight_api(user_arguments_list)

#call flight API and get flight data
flight_api_call = requests.get( url )
flight_api_status_code = flight_api_call
flight_api_response_text = flight_api_call.text
flight_data_dict = json.loads(flight_api_response_text)

#check if flight was founded
try:
	data = (flight_data_dict["data"])[0]
except Exception as err:
	if logging==1:
		print('ERR: No flight founded! ')
	print('0')
	quit()

# compose book api url
json_of_book_api_arguments = compose_arg_json_for_book_api(flight_data_dict, user_arguments_list)

#call book API 
book_api_call = requests.post ( book_api_server + "booking",json=json_of_book_api_arguments )

#print output
if "200" in str(book_api_call):
	book_output_json = json.loads(book_api_call.text)
	reservation_code = book_output_json["pnr"]
	if logging == 1:
		print('Your book reservation ticket code: ') 
	print(reservation_code)
else:
	print(0)

