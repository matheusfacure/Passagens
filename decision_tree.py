import sys
from time import time
sys.path.append("./tools/")
from pprint import pprint as pp
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cross_validation import train_test_split
from sklearn import tree, grid_search
from sklearn.ensemble import AdaBoostRegressor
from sklearn.learning_curve import learning_curve

from process_skyscanner import load_CSVs, data_split
from plot_learning_curve import plot_learning_curve
from tranfs_train_test import test_regr, applyPCA, remove_outliers



# carrega os arquvios
t0 = time()

var_list= ['preco', 'col_wday', 'col_hour', 'col_yday', 'out_stop1', 'in_stop1', 
 'agent', 'out_orStat', 'out_desStat', 'ag_type', 'in_carr1', 'out_carr1',
 'out_chegada', 'out_saida', 'in_saida', 'in_chegada']

path = '/media/matheus/EC2604622604305E/data/Passagens/CSV_Format/BSB-VCP*.csv'
df = load_CSVs(path, var_list, max_files = 5, n_days = 2)
print("Tempo para carregar os dados:", round(time()-t0, 3), "s\n")
print('Dias de coleta selecionados: ', df.col_yday.unique())
# pp(df.columns.to_series().groupby(df.dtypes).groups)
	

# novas variáveis
t0 = time()
print('Adicionando novas variáveis')

# variáveis de tempo
for t_var in ['out_chegada', 'out_saida', 'in_saida', 'in_chegada']:
	df[t_var] = pd.to_datetime(df[t_var], format='%Y-%m-%d %H:%M:%S')
	df[t_var + '_hour'] = df[t_var].dt.hour
	df[t_var + '_yday'] = df[t_var].dt.day

	df[t_var + '_wday'] = df[t_var].dt.dayofweek
	df[t_var + '_wday'] = df[t_var + '_wday'].astype('category')
	df[t_var + '_is_wend'] = df[t_var].dt.dayofweek > 4
	
	df.drop(t_var, axis = 1, inplace = True)


df = pd.get_dummies(df)



# lidando com NaNs
for var in df.columns:
	n_nans = sum(pd.isnull(df[var]))

df = df.fillna(0)
print("Dimensões da matriz: ", df.shape)



# separando treino e teste
#train, test = data_split(df, 2)
train, test = train_test_split(df, test_size = 0.2, random_state = 123)
y_train, y_test = train['preco'], test['preco']
X_train, X_test = train.drop('preco', 1), test.drop('preco', 1)


# trasfonrma dia da coleta em delta d_coleta d_viagem
X_train['col_yday'] =  X_train['out_saida_yday'] - X_train['col_yday']
X_train.drop('col_yday', axis = 1, inplace = True)
X_test['col_yday'] =  X_test['out_saida_yday'] - X_test['col_yday']
X_test.drop('col_yday', axis = 1, inplace = True)


# lindando com outliers
X_train, y_train = remove_outliers(X_train, y_train, n_std = 3, verbose = True)


# PCA
X_train, X_test = applyPCA(X_train, X_test, 40)

print('Tempo para filtrar os dados:', round(time()-t0, 3), 's\n')
print('Dimensões da matriz após filtrar:' , X_train.shape)


# faz o regressor
print('\nTreinando uma árvore de decisão otimizada com busca euxaustiva de '\
			   'parâmetros...\n')

parameters = {'min_samples_split': [25, 50, 100],
			   'max_depth': [15, 25, 35]}
#regr = grid_search.GridSearchCV(tree.DecisionTreeRegressor(), parameters)
regr = tree.DecisionTreeRegressor(min_samples_split = 5, max_depth = 25)


# plotando curvas de aprendizagem
# t0 = time()
# title = "Learning Curves"
# plot_learning_curve(regr, title, X_train, y_train, cv = 5, n_jobs=4)
# print('Tempo para plotar as curvas:', round(time()-t0, 3), 's\n')
#plt.show()


# treinando e testando o regressor
t0 = time()
regr = regr.fit(X_train, y_train)
print("Resultados: \nTempo para treinar:", round(time()-t0, 3), "s")
test_regr(regr, X_test, y_test)



# faz o regressor
print('\nTreinando uma árvore de decisão otimizada com boosting')
regr = tree.DecisionTreeRegressor(min_samples_split = 25, max_depth = 15)
regr = AdaBoostRegressor(regr, n_estimators = 500)

# treinando e testando o regressor
regr = regr.fit(X_train, y_train)
print("Resultados: \nTempo para treinar:", round(time()-t0, 3), "s")
test_regr(regr, X_test, y_test)
