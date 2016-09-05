import simplejson as json
import datetime as dt
import time
import re
from pprint import pprint as pp


def clean_none(data):
	new_data = []
	for i in data:
		if i is None:
			continue
		new_data.append(i)
	return new_data
	

def process_itinerary(dicio):
	print(dicio.keys())
	itineraries = dicio['Itineraries']
	
	# limpa o texto e retira informações irrelevantes
	itineraries_list = []
	for itinerarie in itineraries:
		InboundLegId = itinerarie['InboundLegId']
		OutboundLegId = itinerarie['OutboundLegId']
		PricingOptions = []
		
		for options in itinerarie['PricingOptions']:
			agents = options['Agents']
			price = options['Price']
			QuoteAgeInMinutes = options['QuoteAgeInMinutes']
			PricingOptions.append([agents, price, QuoteAgeInMinutes])
		
		itineraries_list.append([InboundLegId, OutboundLegId, PricingOptions])

	return itineraries_list # InboundLegId, OutboundLegId, agents, price, QAgInMin




file = 'BSB-VCP-201610191458-201610191458.json'

with open(file, 'r') as fp:
	data = json.load(fp)

data = clean_none(data)

pdata = process_itinerary(data[0])

pp(pdata[0])