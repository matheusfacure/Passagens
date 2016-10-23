import sys
from time import time
sys.path.append("./tools/")
from pprint import pprint as pp
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import AdaBoostClassifier, RandomForestRegressor
from sklearn.metrics import mean_squared_error


from process_skyscanner import load_CSVs, data_split
from plot_learning_curve import plot_learning_curve
from tranfs_train_test import test_regr, applyPCA, remove_outliers
np.random.seed(123)


# carrega os arquvios
t0 = time()

var_list= ['preco', 'vid','ag_nome', 'ag_type',
	 'out_saida', 'out_chegada', 'out_stops', 
	 'in_saida', 'in_chegada', 'in_stops',
	 't_delta_ida', 'dura_viagem', 'col_wday', 'col_yday']

path = '/media/matheus/Elements/data/Passagens/CSV_Format/BSB-VCP*.csv'
df = load_CSVs(path, var_list, n_days = 35)
print("Tempo para carregar os dados:", round(time()-t0, 3), "s\n")
print('Dias de coleta selecionados: ', df.col_yday.unique())


t0 = time()

#filtrando 
df = df[df['ag_type'] == 'Airline']
df.drop('ag_type', axis = 1, inplace = True)
df = df[df['dura_viagem'] < 5]
# novas variáveis

#variáveis de tempo
for t_var in ['out_chegada', 'out_saida', 'in_saida', 'in_chegada']:

	df[t_var] = pd.to_datetime(df[t_var], format='%Y-%m-%d %H:%M:%S')
	
	# df[t_var + '_hour'] = df[t_var].dt.hour
	df[t_var + '_yday'] = df[t_var].dt.day

	df[t_var + '_wday'] = df[t_var].dt.dayofweek
	#df[t_var + '_wday'] = df[t_var + '_wday'].astype('category')
	df[t_var + '_is_wend'] = df[t_var].dt.dayofweek > 4
	df.drop(t_var, axis = 1, inplace = True)

df = df[df['out_saida_wday'] > 4]

# print(df.head())
df = pd.get_dummies(df, columns = ['ag_nome', 'ag_type'], drop_first=True)

#train, test = data_split(df, shuffle = True, test_stize = 0.2)
train, test = data_split(df, shuffle = False)
y_train, y_test = train['preco'], test['preco']
X_train, X_test = train.drop('preco', 1), test.drop('preco', 1)

# lindando com outliers
X_train, y_train = remove_outliers(X_train, y_train, n_std = 3, verbose = False)

print('Tempo para filtrar os dados:', round(time()-t0, 3), 's\n')


# PCA
#X_train, X_test = applyPCA(X_train, X_test, 10, verbose = False)

#n =  int(X_train.shape[0]/200)

#faz o regressor
regr = RandomForestRegressor(max_depth = 25,
		warm_start = True, random_state = 2, n_jobs = -1, n_estimators = 100)


# Testa e treina o regressor
print('Treinando o a arvore de decisão')
t0 = time()
regr = regr.fit(X_train, y_train)
print("Resultados: \nTempo para treinar:", round(time()-t0, 3), "s")
test_regr(regr, X_train, y_train, X_test, y_test)

