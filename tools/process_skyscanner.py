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
	

def add_place_info_to_row(dicio, row, row_station):
	for place in dicio['Places']:
			if place['Id'] == row[row_station]:
				row.append(place['Name'])
				row.append(place['Type'])


def json_to_lists(dicio):
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

	# limpa os lags e adiciona infos relevantes às observações
	for row in rows:
		for leg in dicio['Legs']:

			# informações sobre a ida
			if leg['Id'] == row[4]: # se o OutId da row e do Lag coincidirem
				add_leg_info_to_row(row, leg)

			# informações sobre a volta
			if leg['Id'] == row[3]: # se o inId da row e do Lag coincidirem
				add_leg_info_to_row(row, leg)
	# row no formato:
	# [preço(0), QAgInMin(1), Agent(2), InId(3), OutId(4),
	# ag_nome(5),  ag_optMobile(6), ag_stat(7), ag_type(8)
	# out_saida(9), out_chegada(10), out_dura(11), out_jMode(12),
	# 	out_orStat(13), out_desStat(14), out_stop1(15), out_stop2(16),
	#	out_stop3(17), out_OpCarr1(18), out_OpCarr2(19), out_OpCarr3(20),
	#	out_carr1(21), out_carr2(22), out_carr3(23)
	# in_saida(24), in_chegada(25), in_dura(26)_, in_jMode(27), in_orStat(28),
	#	in_desStat(29), in_stop1(30), in_stop2(31), in_stop3(32),
	#	in_OpCarr1(33), in_OpCarr2(34), in_OpCarr3(35), in_carr1(36),
	#	in_carr2(37), in_carr3(38)]

	# limpa os places e adiciona infos relevantes às observações
	for row in rows:
		add_place_info_to_row(dicio, row, 13)
		add_place_info_to_row(dicio, row, 14)
		add_place_info_to_row(dicio, row, 28)
		add_place_info_to_row(dicio, row, 29)
	# row no formato:
	# row + [ida_or_nome(39), ida_or_tipo(40), ida_dest_nome(41),
	#	ida_dest_tipo(42)
	# volta_or_nome(42), volta_or_tipo(44), volta_dest_nome(45),
	#	volta_dest_tipo(46)]

	# limpa os places e adiciona infos relevantes às observações
	for row in rows:
		for t_coleta in dicio['hora_coleta']:
			row.append(t_coleta)
	# row no formato:
	# row + [col_year(47), col_mon(48), col_mday(49), col_hour(50), col_min(51),
	#	col_sec(52), col_wday(53), col_yday(54), col_isds(55)
	
	return rows


def process(jsons):
	data = clean_none(jsons)

	table = np.array(json_to_lists(data[0]))
	for dicio in data:
		arr = np.array(json_to_lists(dicio))
		table = np.concatenate((table, arr), axis=0)

	print(table)

if __name__ == '__main__':

	file = 'BSB-VCP-201612131212-201612131212.json'

	with open(file, 'r') as fp:
		data = json.load(fp)

	pdata = process(data)


