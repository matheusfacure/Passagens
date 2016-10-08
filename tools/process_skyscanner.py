import simplejson as json
import datetime as dt
import time
import re
import numpy as np
import pandas as pd
from sys import argv, exit
from glob import glob
from pprint import pprint as pp
import random
random.seed(321)

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
	row.append(len(leg['Stops']))

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
		p_count = 0
		for option in itinerarie['PricingOptions']:
			for agent in option['Agents']:
				row = []
				row.append(option['Price']) # add preço
				p_count += 1 
				row.append(option['QuoteAgeInMinutes']) # add QAgeInMin
				row.append(agent)
				row.append(itinerarie['InboundLegId'])						 
				row.append(itinerarie['OutboundLegId'])
				rows.append(row)
			
			if p_count > 5:
				break
		if p_count > 5:
				break


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
	# 	out_orStat(13), out_desStat(14), out_stops(15), out_stop1(16),
	#	out_stop2(17), out_stop3(18), out_OpCarr1(19), out_OpCarr2(20),
	#	out_OpCarr3(21), out_carr1(22), out_carr2(23), out_carr3(24)
	# in_saida(25), in_chegada(26), in_dura(27)_, in_jMode(28), in_orStat(29),
	#	in_desStat(30), out_stops(31), in_stop1(32), in_stop2(33), in_stop3(34),
	#	in_OpCarr1(35), in_OpCarr2(36), in_OpCarr3(37), in_carr1(38),
	#	in_carr2(39), in_carr3(40)]
		

	# limpa os places e adiciona infos relevantes às observações
	for row in rows:
		add_place_info_to_row(dicio, row, 13)
		add_place_info_to_row(dicio, row, 14)

		if volta_check:
			add_place_info_to_row(dicio, row, 29)
			add_place_info_to_row(dicio, row, 30)
		else:
			for unused in range(4):
				row.append('NaN')

	# row no formato:
	# row + [ida_or_nome(41), ida_or_tipo(42), ida_dest_nome(43),
	#	ida_dest_tipo(44)
	# volta_or_nome(45), volta_or_tipo(46), volta_dest_nome(47),
	#	volta_dest_tipo(48)]

	# tempo de coleta e adiciona infos relevantes às observações
	for row in rows:
		t = dicio['hora_coleta']
		t_col = dt.datetime(t[0], t[1], t[2], t[3], t[4], t[5])
		row.append(t_col)

		t_ida = time.strptime(row[9], "%Y-%m-%dT%H:%M:%S")
		t_ida = dt.datetime(*t_ida[0:6])
		t_delta_ida = t_ida - t_col
		row.append(t_delta_ida.days)

		t_volta = time.strptime(row[25], "%Y-%m-%dT%H:%M:%S")
		t_volta = dt.datetime(*t_volta[0:6])
		dura_viagem = t_volta - t_ida
		row.append(dura_viagem.days)
		
		for t_coleta in dicio['hora_coleta'][6:]:
			row.append(t_coleta)

	
	# row no formato:
	# row + [col_time(49), t_delta_ida(50), dura_viagem(51), col_wday(50),
	# col_yday(51), col_isds(52)]
	
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
		'out_desStat', 'out_stops', 'out_stop1', 'out_stop2', 'out_stop3',
		'out_opCarr1','out_opCarr2', 'out_opCarr3', 'out_carr1', 'out_carr2',
		'out_carr3',
	 'in_saida', 'in_chegada', 'in_dura', 'in_jMode', 'in_orStat', 'in_desStat',
		'in_stops', 'in_stop1', 'in_stop2', 'in_stop3', 'in_opCarr1',
		'in_opCarr2', 'in_opCarr3', 'in_carr1', 'in_carr2', 'in_carr3',
	 'ida_or_nome', 'ida_or_tipo', 'ida_dest_nome', 'ida_dest_tipo',
	 'volta_or_nome', 'volta_or_tipo', 'volta_dest_nome', 'volta_dest_tipo',
	 'col_time', 't_delta_ida', 'dura_viagem', 'col_wday', 'col_yday',
	 'col_isds']

	return df


def load_CSVs(path, var_list, max_files='All', n_days = 5):
	# defensivo
	if 'col_yday' not in var_list:
		print('col_yday deve estar na lista de variáveis.')
		exit(1)

	allFiles = glob(path)
	random.shuffle(allFiles)

	if max_files != 'All':
		allFiles = allFiles[:max_files]
	print("Carregando %d dia(s)..." % n_days)
	frame = pd.DataFrame()
	list_ = []

	categ_var = ['ag_type', 'agent', 'out_orStat', 'out_desStat', 'out_opCarr1',
		'out_opCarr2', 'out_opCarr3', 'in_opCarr1', 'in_opCarr2', 'in_opCarr3',
		'in_orStat', 'in_desStat', 'in_carr1', 'in_carr2', 'in_carr3',
		'out_carr1', 'out_carr2', 'out_carr3', 'in_jMode', 'out_jMode',
		'in_orStat', 'ida_or_nome', 'ida_or_tipo', 'ida_dest_tipo',
		'ida_dest_nome', 'volta_or_nome', 'volta_or_tipo', 'volta_dest_tipo',
		'volta_dest_nome', 'ag_nome', 'ag_stat', 'in_stop1', 'in_stop2',
		'in_stop3', 'out_stop1', 'out_stop2', 'out_stop3']
	
	date_time_var = ['out_saida', 'out_chegada', 'in_saida', 'in_chegada']
	
	seen_days = []
	while len(seen_days) + 1 <= n_days:
		file = allFiles.pop()

		# defensivo
		if file[-4:] != '.csv':
			print('Arquivo %s não é do formato esperado' % file)
			print("Arquivo deve ser uma df no formato csv, sep = ';'")
			exit(1)

		df = pd.read_csv(file, sep = ';', header=0)
			
		df = df[var_list] # seleciona apenas variáveis especificadas
			
		if df.col_yday.unique()[0] not in seen_days:
			seen_days.append(df.col_yday.unique()[0])

		list_.append(df)

	frame = pd.concat(list_, ignore_index=True)
		
	vars_in_frame = frame.columns
	# converte para os tipos certos
	for var in categ_var:
		if var in vars_in_frame:
			frame[var] = frame[var].astype('category')

	for var in date_time_var:
		if var in vars_in_frame:
			frame[var] = np.array(frame[var], dtype='datetime64')
	return frame


def data_split(frame, shuffle = False, test_stize = 0.2, test_days = 1):
	
	if shuffle:
		frame = frame.iloc[np.random.permutation(len(frame))]
		frame = frame.reset_index(drop=True)
		if test_stize > 1 or test_stize < 0:
			print('Tamanho do set de teste deve ser no máximo 1')
			exit(1)

		msk = np.random.rand(len(frame)) <  1 - test_stize
		train = frame[msk]
		test = frame[~msk]
	
	else:
		frame.sort_values(by=['col_yday'], ascending=[True], inplace = True)
		days = frame.col_yday.unique()
		print(days)

		print(days[-test_days:])
		test = frame.loc[frame['col_yday'].isin(days[-test_days:])]
		train = frame.loc[~frame['col_yday'].isin(days[-test_days:])]

	return train, test


def make_folds(training_df, folds = 3):
	
	days = training_df.col_yday.unique()
	n_days = len(days)

	train = []

	# faz os folds
	if folds and n_days > 2 and n_days % folds == 0:
		days_per_fold = int(n_days / folds)
		for i in range(0, n_days, days_per_fold):
			
			sv = (training_df['col_yday'] >= days[i]) 
			sv = sv & (training_df['col_yday'] <= days[i + days_per_fold - 1])
			print('Fold: ', training_df[sv].col_yday.unique())
			train.append(training_df[sv])

	else:
		print('Não conseguiu criar os folds')
		return training_df

	return train 




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


