from skyscanner.skyscanner import Flights
import simplejson as json
import datetime as dt
import numpy as np
import pandas as pd
import re

def scrape_skyscanner(origem, destino, ida, volta):
	flights_service = Flights('Key')
	result = flights_service.get_result(
		country = 'BR',
		currency = 'BRL',
		locale = 'pt-BR',
		originplace = origem + '-sky',
		destinationplace = destino + '-sky',
		outbounddate = ida,
		inbounddate = volta,
		adults = 1).parsed
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

output = scrape_skyscanner('GRU', 'GIG', '2016-08-25', '2016-08-28')

with open('data.txt', 'w') as outfile:
    json.dump(output, outfile)