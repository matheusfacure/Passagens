import simplejson as json
import datetime as dt
import time
import re
import numpy as np
import pandas as pd
from sys import argv, exit
from glob import glob
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
				row.append('NaN')
			else:
				row.append(leg['Stops'][i])
		else:
			row.append('NaN')

	for i in range(3):
		if len(leg['OperatingCarriers']) >= i + 1:
			row.append(leg['OperatingCarriers'][i])
		else:
			row.append('NaN')

	for i in range(3):
		if len(leg['Carriers']) >= i + 1:
			row.append(leg['Carriers'][i])
		else:
			row.append('NaN')


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
	volta_check = False
	for row in rows:
		
		for leg in dicio['Legs']:

			# informações sobre a ida
			if leg['Id'] == row[4]: # se o OutId da row e do Lag coincidirem
				add_leg_info_to_row(row, leg)
				
				# achamos a ida, agora procuramos a volta
				# Obs: nem sempre há volta
				for volta_leg in dicio['Legs']:

					# informações sobre a volta (Obs: nem sempre há volta)
					if volta_leg['Id'] == row[3]:
						add_leg_info_to_row(row, volta_leg)
						volta_check = True

				# Se não acharmos uma volta, adicionamos zeros
				if not volta_check:
					for unused in range(15):
						row.append('NaN')

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

		if volta_check:
			add_place_info_to_row(dicio, row, 28)
			add_place_info_to_row(dicio, row, 29)
		else:
			for unused in range(4):
				row.append('NaN')

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
	#	col_sec(52), col_wday(53), col_yday(54), col_isds(55)]
	
	return rows


def process(jsons):
	data = clean_none(jsons)

	table = np.array(json_to_lists(data[0]))

	# verifica se o primeiro array da tabela não é vazio
	# so continua quando começar a tabela com um array != de zero
	i = 1
	while table.shape[0] == 0:
		table = np.array(json_to_lists(data[i]))
		i += 1


	for dicio in data:
				
		# se não tivermos nenhuma viagem no dicio
		if dicio['Itineraries'] == []:
			continue
		
		arr = np.array(json_to_lists(dicio))
		table = np.concatenate((table, arr), axis=0)

	df = pd.DataFrame(table)
	df.columns = ['preco', 'qAgInMin', 'agent', 'inId', 'outId', 'ag_nome',
	 'ag_optMobile', 'ag_stat', 'ag_type',
	 'out_saida', 'out_chegada', 'out_dura', 'out_jMode', 'out_orStat',
		'out_desStat', 'out_stop1', 'out_stop2', 'out_stop3', 'out_opCarr1',
		'out_opCarr2', 'out_opCarr3', 'out_carr1', 'out_carr2', 'out_carr3',
	 'in_saida', 'in_chegada', 'in_dura', 'in_jMode', 'in_orStat', 'in_desStat',
		'in_stop1', 'in_stop2', 'in_stop3', 'in_opCarr1', 'in_opCarr2',
		'in_opCarr3', 'in_carr1', 'in_carr2', 'in_carr3',
	 'ida_or_nome', 'ida_or_tipo', 'ida_dest_nome', 'ida_dest_tipo',
	 'volta_or_nome', 'volta_or_tipo', 'volta_dest_nome', 'volta_dest_tipo',
	 'col_year', 'col_mon', 'col_mday', 'col_hour', 'col_min', 'col_sec',
	  'col_wday', 'col_yday', 'col_isds']



	
	return df


def load_CSVs(path):
	allFiles = glob(path)
	frame = pd.DataFrame()
	list_ = []
	for file_ in allFiles:
		
		if file_[-4:] != '.csv':
			print('Arquivo %s não é do formato esperado' % file_)
			print("Arquivo deve ser uma df no formato csv, sep = ';'")
			exit(1)

		df = pd.read_csv(file_, sep = ';', header=0)
		list_.append(df)
	frame = pd.concat(list_, ignore_index=True)

	# converte para os tipos certos
	categ_var = ['ag_type', 'agent', 'out_orStat', 'out_desStat', 'out_opCarr1',
		'out_opCarr2', 'out_opCarr3', 'in_opCarr1', 'in_opCarr2', 'in_opCarr3',
		'in_orStat', 'in_desStat', 'in_carr1', 'in_carr2', 'in_carr3',
		'out_carr1', 'out_carr2', 'out_carr3', 'in_jMode', 'out_jMode',
		'in_orStat', 'ida_or_nome', 'ida_or_tipo', 'ida_dest_tipo',
		'ida_dest_nome', 'volta_or_nome', 'volta_or_tipo', 'volta_dest_tipo',
		'volta_dest_nome', 'ag_nome', 'ag_stat']

	for var in categ_var:
		frame[var] = df[var].astype('category')

	date_time_var = ['out_saida', 'out_chegada', 'in_saida', 'in_chegada']

	for var in date_time_var:
		frame[var] = np.array(frame[var], dtype='datetime64')

	return frame




if __name__ == '__main__':

		
	files = argv[1:] # pega os arquivos
	for file in files:
		
		# ensure proper usage
		if file[-5:] != '.json':
			print('Uso: \n `python3 skyscannerfile.json` ou\n '\
				'`python3 *.json` ')
			print('Arquivo %s não é do formato esperado' % file)
			exit(1)

		# lê o arquivo
		with open(file, 'r') as in_file:
			data = json.load(in_file)


		# processa os dados em uma data frame
		print('\nProcessando %s ...' % file)
		t0 = time.time()
		pdata = process(data)
		print('Tempo para processar %s:' % file, round(time.time()-t0, 3), 's')

		# salva em csv
		out_file = file[0:-5] + '.csv'
		print('\nSalvando %s ...' % out_file)

		t0 = time.time()
		pdata.to_csv(out_file, sep = ';', date_format = '%Y', index = False)
		print('Tempo para salvar %s:' % out_file, round(time.time()-t0, 3), 's')
		print('\n')


