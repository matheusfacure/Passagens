import sys
from time import time
sys.path.append("./tools/")
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from process_skyscanner import load_CSVs, data_split
from tranfs_train_test import test_regr
np.random.seed(123)

class random_walk(object):

	def __init__(self):
		pass


	def fit(self, X_train, y_train):
		
		X_train = pd.DataFrame(X_train)
		X_train['label'] =  y_train

		assert 'vid' in X_train.columns
		assert 'col_yday' in X_train.columns

		self.pred_dict = {}

		# para cada voo identificado
		for i, voo_id in enumerate(X_train['vid'].unique()):

			# restringe a busca na df ao voo identificado
			temp_df = X_train[X_train['vid'] == voo_id]

			# restringe a busca na df ao último dia
			temp_df[temp_df['col_yday'] == temp_df['col_yday'].max()]
			
			# acha a média dos voos identificados no último dia
			pred_price = temp_df['label'].mean()
			self.pred_dict[voo_id] = pred_price


	def predict(self, X_test):
		X_test = pd.DataFrame(X_test)

		y_pred = []
		self.nao_vistos = 0

		mean_price = np.mean(list(self.pred_dict.values()))

		for voo_id in X_test['vid']:

			# se o voo já foi observado
			if voo_id in self.pred_dict:
				y_pred.append(self.pred_dict[voo_id])

			# se o voo não foi observado
			else:
				y_pred.append(mean_price)
				self.nao_vistos += 1

		return np.array(y_pred)


	def get_params(self):
		return 'None'


if __name__ == '__main__':

	t0 = time()
	var_list= ['preco', 'vid', 'col_yday']

	path = '/media/matheus/Elements/data/Passagens/CSV_Format/BSB-VCP*.csv'
	df = load_CSVs(path, var_list, n_days = 10)
	print("Tempo para carregar os dados:", round(time()-t0, 3), "s\n")
	print('Dias de coleta selecionados: ', df.col_yday.unique())

	train, test = data_split(df, shuffle = False, test_days = 3)
	y_train, y_test = train['preco'], test['preco']
	X_train, X_test = train.drop('preco', 1), test.drop('preco', 1)

	print('Treinando o random walk')
	t0 = time()
	regr = random_walk()
	regr.fit(X_train, y_train)
	print("Resultados: \nTempo para treinar:", round(time()-t0, 3), "s")
	test_regr(regr, X_train, y_train, X_test, y_test)
	print('Dias não vistos:', regr.nao_vistos)