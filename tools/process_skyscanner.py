import simplejson as json
import datetime as dt
import time
import re
import numpy as np
import pandas as pd

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
	rows = []
	for itinerarie in itineraries:
		for option in itinerarie['PricingOptions']:
			for agent in option['Agents']:
				row = []
				row.append(option['Price']) # add preço
				row.append(option['QuoteAgeInMinutes']) # add QAgeInMin
				row.append(agent)
				row.append(itinerarie['InboundLegId'])						 
				row.append(itinerarie['OutboundLegId'])
				rows.append(row)
	return rows



file = 'BSB-VCP-201612131212-201612131212.json'

with open(file, 'r') as fp:
	data = json.load(fp)

print(len(data))
data = clean_none(data)
print(len(data))

pdata = process_itinerary(data[0])
#pp(data[0])
pp(pdata)