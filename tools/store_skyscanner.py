from skyscanner.skyscanner import Flights
import simplejson as json
import datetime as dt
import time
import re


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

	def __str__(self):
		s = 'Origens: ' + ' ; '.join(self.origens) + '\n'
		s += 'Destinos: ' + ' ; '.join(self.destinos) + '\n'
		s += 'Idas: ' +  ' ; '.join(self.idas) + '\n'
		s += 'Voltas: ' + ' ; '.join(self.voltas) + '\n'
		return s

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
						json_dic = None

					json_list.append(json_dic)

	print('O objeto de coleta foi: ', vgns)
	return json_list



comeco = dt.datetime.today() + dt.timedelta(days = 1) # amanhã

# 2 em 2 dias, curto prazo
fim = comeco + dt.timedelta(days = 50)
viagens = vgns(['BSB'], ['VCP'], comeco, fim, 2)

# 5 em 5 dias, médio prazo
fim1 = comeco + dt.timedelta(days = 100)
viagens1 = vgns(['BSB'], ['VCP'], comeco, fim1, 5)
viagens2 = vgns(['GRU', 'VCP'], ['CFN','MAO', 'GIG'], comeco, fim1, 5)

# 10 em 10 dias, longo prazo
fim2 = comeco + dt.timedelta(days = 200)
viagens3 = vgns(['GRU'], ['JFK','LIM', 'TXL', 'TPE'], comeco, fim2, 10)

# coletar viagens
viagens_list = [viagens, viagens1, viagens2, viagens3]
for v in viagens_list:
	output = scrape_skyscanner_vgns(v)
	file = viagens.identidade + '.json'

	with open(file, 'w') as outfile:
		json.dump(output, outfile)
	

