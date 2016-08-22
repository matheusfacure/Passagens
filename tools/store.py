from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import re
import datetime as dt


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

wd = webdriver.Firefox()

texto = get_decolar_text('BSB', 'VCP', '2016-09-08', '2016-10-08')
process_decolar_text(texto)