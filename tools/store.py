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


def process_decolar_line(linha):

	preco = re.findall(r'R\$ ?\d?\d?\.?\d\d\d', linha)[0][3:]
	preco = int(re.sub(r'\.', '', preco))

	print(preco)


def process_decolar_text(decolar_text):
	if decolar_text == None:
		return decolar_text

	linhas = decolar_text.split('IDA\n')[1:]
	dados_decolar = []
	for linha in linhas:
		process_decolar_line(linha)

wd = webdriver.Firefox()

texto = get_decolar_text('BSB', 'VCP', '2016-09-08', '2016-10-08')
process_decolar_text(texto)