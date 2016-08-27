from skyscanner.skyscanner import Flights
import simplejson as json
import datetime as dt
import numpy as np
import pandas as pd
import re
import time
from pprint import pprint as pp


def scrape_skyscanner(origem, destino, ida, volta):
	flights_service = Flights('key')
	result = flights_service.get_result(
		country = 'BR',
		currency = 'BRL',
		locale = 'pt-BR',
		originplace = origem + '-sky',
		destinationplace = destino + '-sky',
		outbounddate = ida,
		inbounddate = volta,
		adults = 1).parsed
	
	result['hora_coleta'] = time.localtime()
	return result

class vgns():
	""" 

	origem, destino, comeco , fim, by = 3
	origems e destinos devem ser siglas oficiais de aeroportos
	comeco e fim devem ser objetos datetime
	by é o intervalo de dias de criação de viagens

	"""
	def __init__(self, origens, destinos, comeco , fim, by = 3):
		
		date_list = []
		while comeco < fim:
			date_list.append(str(comeco)[:10])
			comeco = comeco + dt.timedelta(days = by)
		
		id_origens = ''.join(origens)
		id_destinos = ''.join(destinos)
		id_comeco = re.sub(r'\W+', '', str(comeco)[:17])
		id_fim = re.sub(r'\W+', '', str(fim)[:17])
		identidade = '-'.join([id_origens, id_destinos, id_comeco, id_fim])
			
		self.origens = origens
		self.destinos = destinos
		self.idas = date_list
		self.voltas = date_list
		self.identidade = identidade

	def __len__(self):
		return len(self.idas)

def  scrape_skyscanner_vgns(vgns):
	json_list = []
	for origem in vgns.origens:
		for destino in vgns.destinos:
			for ida in vgns.idas:
				for volta in vgns.voltas:

					# pulando algumas iterações
					ida_tm = time.strptime(ida, "%Y-%m-%d")
					volta_tm = time.strptime(volta, "%Y-%m-%d")
					if ida_tm > volta_tm:
						continue
					if origem == destino:
						continue

					print('\n\n Coletando: ', origem, destino, ida, volta)
					try:
						json_dic = scrape_skyscanner(origem, destino,
							ida, volta)
					except:
						print('Erro ao Coletar: ', origem, destino, ida, volta)
					
					json_list.append(json_dic)		
	return json_list



comeco = dt.datetime.today() + dt.timedelta(days = 1)
fim = comeco + dt.timedelta(days = 5)
viagens = vgns(['BSB'], ['VCP'], comeco, fim, 3)

output = scrape_skyscanner_vgns(viagens)


with open('data.json', 'w') as outfile:
    json.dump(output, outfile)


with open('data.json', 'r') as fp:
    data = json.load(fp)


pp(data)