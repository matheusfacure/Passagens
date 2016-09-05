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
	
def add_leg_info_to_row(row, leg):
	row.append(leg['Departure'])
	row.append(leg['Arrival'])
	row.append(leg['Duration'])
	row.append(leg['JourneyMode'])
	row.append(leg['OriginStation'])
	row.append(leg['DestinationStation'])
				
	for i in range(3):
		if len(leg['Stops']) >= i + 1:
			if leg['Stops'][i] is None:
				row.append(0)
			else:
				row.append(leg['Stops'][i])
		else:
			row.append(0)

	for i in range(3):
		if len(leg['OperatingCarriers']) >= i + 1:
			row.append(leg['OperatingCarriers'][i])
		else:
			row.append(0)

	for i in range(3):
		if len(leg['Carriers']) >= i + 1:
			row.append(leg['Carriers'][i])
		else:
			row.append(0)
	


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
	# [preço, QAgInMin, Agent, InId, OutId]


	# limpa os agentes e adiciona infos relevantes às observações
	for row in rows:
		for agent in dicio['Agents']:
			if agent['Id'] == row[2]: # se o Id da row e do agente coincidirem
				row.append(agent['Name'])
				row.append(agent['OptimisedForMobile'])
				row.append(agent['Status'])
				row.append(agent['Type'])
	# row no formato:
	# [preço, QAgInMin, Agent, InId, OutId,
	# ag_nome,  ag_optMobile, ag_stat, ag_type]


	# limpa os agentes e adiciona infos relevantes às observações
	for row in rows:
		for leg in dicio['Legs']:

			# informações sobre a ida
			if leg['Id'] == row[4]: # se o OutId da row e do Lag coincidirem
				add_leg_info_to_row(row, leg)

			# informações sobre a volta
			if leg['Id'] == row[3]: # se o inId da row e do Lag coincidirem
				add_leg_info_to_row(row, leg)
	# row no formato:
	# [preço, QAgInMin, Agent, InId, OutId,
	# ag_nome,  ag_optMobile, ag_stat, ag_type
	# out_saida, out_chegada, out_dura, out_jMode, out_orStat, out_desStat,
	#	out_stop1, out_stop2, out_stop3, out_OpCarr1, out_OpCarr2, out_OpCarr3,
	#	out_carr1, out_carr2, out_carr3



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