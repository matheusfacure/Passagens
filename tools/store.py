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
			text = wd.find_element_by_id('clusters').text # pega o texto da tabela
		except:
			text = None

		return text

wd = webdriver.Firefox()

texto = get_decolar_text('BSB', 'VCP', '2016-09-08', '2016-10-08')
print(texto)