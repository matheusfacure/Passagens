from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import re
import datetime as dt
import numpy as np
import pandas as pd


def get_decolar_text(origem, destino, ida, volta):
		link = 'http://www.decolar.com/shop/flights/results/roundtrip/'
		link += '/'.join((origem, destino, ida, volta))
		link += '/1/0/0'
		wd.get(link)
		try:
			text = wd.find_element_by_id('clusters').text 
		except:
			text = None
		return text


def process_trechos(trechos):
	horas = trechos.split('Detalhe')[:-1] # separa idas possíveis
	horas_limpas = []

	for h in horas:
		hora = re.findall(r'\d\d:\d\d', h)
		sai = int(hora[0][0:2])*60 #+ int(hora[0][3:])
		chega = int(hora[1][0:2])*60 + int(hora[1][3:])
		horas_limpas.append([sai, chega])
	
	return horas_limpas


def process_decolar_line(linha):

	preco = re.findall(r'R\$ ?\d?\d?\.?\d\d\d', linha)[0][3:]
	preco = int(re.sub(r'\.', '', preco))

	p = re.compile(r'[A-Z][a-z][a-z] \d?\d(.+?)VOLTA', flags=re.DOTALL)
	ida = p.findall(linha)[0]
	idas_limpas = process_trechos(ida)

	p = re.compile(r'VOLTA(.+?)Preço por adulto', flags=re.DOTALL)
	volta = p.findall(linha)[0]
	voltas_limpas = process_trechos(volta)

	return preco, idas_limpas, voltas_limpas


def process_decolar_text(decolar_text):
	if decolar_text == None:
		return decolar_text

	linhas = decolar_text.split('IDA\n')[1:]
	dados_decolar = []
	for linha in linhas:
		preco, idas, voltas = process_decolar_line(linha)

		# colar idas e voltas possíveis
		for ida in idas:
			for volta in voltas:
				row = [preco] + ida + volta
				dados_decolar.append(row)
	return np.array(dados_decolar)


def add_dateCol(date_touple, df):
	df_list = [df]
	for i in date_touple: # data da ida
		df_list.append(pd.DataFrame(np.repeat(i, len(df.index))))
	return	pd.concat(df_list, axis = 1)

def scrape_decolar(origem, destino, ida, volta):
	texto = get_decolar_text(origem, destino, ida, volta)
	
	dados_df = pd.DataFrame(process_decolar_text(texto))

	dados_df = add_dateCol(time.strptime(ida, '%Y-%m-%d')[:3],
		dados_df)

	dados_df = add_dateCol(time.strptime(volta, '%Y-%m-%d')[:3],
		dados_df)

	dados_df = add_dateCol(time.localtime(time.time())[:5],
		dados_df)

	origem_df = pd.DataFrame(np.repeat(origem, len(dados_df.index)))
	destino_df = pd.DataFrame(np.repeat(destino, len(dados_df.index)))

	dados_df = pd.concat([dados_df, origem_df, destino_df], axis = 1)

	dados_df.columns = ('preco', 'sai_ida', 'chega_ida', 'sai_volta',
		'chega_volta', 'ano_ida', 'mes_ida', 'dia_ida', 'ano_volta',
		 'mes_volta', 'dia_volta', 'ano_coleta', 'mes_coleta', 'dia_coleta', 
		 'hora_coleta', 'min_coleta', 'origem', 'destino') 
 
	return dados_df
	

class vgns():
	""" 

	origem, destino, comeco , fim, by = 3
	origems e destinos devem ser siglas oficiais de aeroportos
	comeco e fim devem ser objetos datetime
	by é o intervalo de dias de criação de viagens

	"""
	def __init__(self, origens, destinos, comeco , fim, by = 3):
		
		date_list = [str(comeco)[:10]]
		for dia in range(0,(fim - comeco).days):
			date_list.append(str(comeco + dt.timedelta(days = by))[:10])
			comeco = comeco + dt.timedelta(days = by)
		self.origens = origens
		self.destinos = destinos
		self.idas = date_list
		self.voltas = date_list

	def __len__(self):
		return len(self.idas)


def scrape_vgsn_decolar(vgns):
	df_list = []
	for origem in vgns.origens:
		for destino in vgns.destinos:
			for ida in vgns.idas:
				for volta in vgns.voltas:

					ida_tm = time.strptime(ida, "%Y-%m-%d")
					volta_tm = time.strptime(volta, "%Y-%m-%d")
					if ida_tm > volta_tm:
						continue

					if origem == destino:
						continue

					print(origem, destino, ida, volta)
					#df_list.append(scrape_decolar(origem, destino, ida, volta))
					

	print(pd.concat(df_list))
		


wd = webdriver.Firefox()

comeco = dt.datetime.today() + dt.timedelta(days = 10)
fim = comeco + dt.timedelta(days = 10)
print(comeco, fim)

viagens = vgns(['SAO'], ['GIG'], comeco, fim, 3)

scrape_vgsn_decolar(viagens)



