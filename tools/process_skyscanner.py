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
	

def process(dicio):
	rows = []

	# limpa o itinerário e retira informações irrelevantes
	for itinerarie in dicio['Itineraries']:
		for option in itinerarie['PricingOptions']:
			for agent in option['Agents']:
				row = []
				row.append(option['Price']) # add preço
				row.append(option['QuoteAgeInMinutes']) # add QAgeInMin
				row.append(agent)
				row.append(itinerarie['InboundLegId'])						 
				row.append(itinerarie['OutboundLegId'])
				rows.append(row)
				# row no formato:
				# preço, QAgInMin, Agent, InId, OuId


	# limpa os agentes e adiciona infos relevantes às observações
	for row in rows:
		for agent in dicio['Agents']:
			if agent['Id'] == row[2]: # se o Id da row e do agente baterem
				row.append(agent['Name'])
				row.append(agent['OptimisedForMobile'])
				row.append(agent['Status'])
				row.append(agent['Type'])


	return rows


if __name__ == '__main__':

	file = 'BSB-VCP-201612131212-201612131212.json'

	with open(file, 'r') as fp:
		data = json.load(fp)

	data = clean_none(data)
	pp(data[0])

	pdata = process(data[0])



	pp(pdata)
	print(data[0].keys())