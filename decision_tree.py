import sys
from time import time
sys.path.append("./tools/")
import datetime as dt
import re
from pprint import pprint as pp
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pandasql
from sklearn.cross_validation import train_test_split
from sklearn.metrics import r2_score
from sklearn import tree, grid_search
from sklearn.ensemble import AdaBoostRegressor
from sklearn.decomposition import PCA

from process_skyscanner import load_CSVs

def test_regr(fit_regr, X_test, y_test):
	t0 = time()	
	pred = fit_regr.predict(X_test)
	print("Tempo para testar:", round(time()-t0, 3), "s")

	r2 = r2_score(y_test, pred)
	print('R² é: %.3f' % r2)

	abs_err = np.abs(y_test - pred)
	print('Erro absoluto médio é: ± R$ %.2f' % np.mean(abs_err))
	print('Desvio padrão do erro absoluto: %.2f' % np.std(abs_err))
	
	err_rel = np.abs((y_test - pred) / y_test) * 100
	print('Erro relativo médio é: %.2f' % np.mean(err_rel), r'%')
	print('Desvio padrão do erro relativo: %.3f\n' % np.std(err_rel))



# carrega os arquvios
t0 = time()
path = '/media/matheus/EC2604622604305E/data/Passagens/CSV_Format/BSB-VCP*.csv'
df = load_CSVs(path, max_files = 5, categ_as_int = True)
print("Tempo para carregar os dados:", round(time()-t0, 3), "s\n")
# pp(df.columns.to_series().groupby(df.dtypes).groups)
	

# Filtra a df apenas com as variáveis selecionadas
t0 = time()

q = """
SELECT preco, col_wday, col_hour, col_yday, out_stop1, in_stop1, 
 agent, out_orStat, out_desStat, ag_type, in_carr1, out_carr1,
 out_chegada, out_saida, in_saida, in_chegada
FROM df
"""
df = pandasql.sqldf(q.lower(), locals())


# cria novas variáveis

# variáveis de tempo
for t_var in ['out_chegada', 'out_saida', 'in_saida', 'in_chegada']:
	df[t_var] = pd.to_datetime(df[t_var], format='%Y-%m-%d %H:%M:%S')
	df[t_var + '_hour'] = df[t_var].dt.hour
	df[t_var + '_wday'] = df[t_var].dt.dayofweek
	df[t_var + '_yday'] = df[t_var].dt.day
	df.drop(t_var, axis=1, inplace=True)

print("Dimensões da matriz: ", df.shape, '\n')

# Pré-processamento
# lida com NaNs
for var in df.columns:
	n_nans = sum(pd.isnull(df[var]))

print('\nSubstituindo os NaNs por %d...' % 0)
df = df.fillna(0)
df = pd.get_dummies(df)

train, test = train_test_split(df, test_size = 0.2, random_state = 123)
y_train, y_test = train['preco'], test['preco']
X_train, X_test = train.drop('preco', 1), test.drop('preco', 1)


# lindando com outliers
top_outliers = y_train > np.mean(y_train) + 3 * np.std(y_train)
print('Temos %d outliers no topo' % sum(top_outliers))
print('Isso equivale à %.3f' % (sum(top_outliers) / len(y_train)), r'%') 
botom_outliers = y_train < np.mean(y_train) - 3 * np.std(y_train)
print('Temos %d outliers na base' % sum(botom_outliers)) 
print('Isso equivale à %.3f' % (sum(botom_outliers) / len(y_train)), r'%') 
tot_outliers = np.logical_not(np.logical_or(botom_outliers, top_outliers))

y_train = y_train[tot_outliers]
X_train = X_train[tot_outliers]


# PCA
n_comp = 15
print('Aplicando alálise de componentes principais (PCA) com %d componentes...'%
	n_comp)
pca = PCA(n_components = n_comp)
pca.fit(X_train)
X_train = pca.transform(X_train)
X_test = pca.transform(X_test)
# print('Componentes principais: ', pca.explained_variance_ratio_ )


print('Tempo para filtrar os dados:', round(time()-t0, 3), 's\n')
print('Dimensões da matriz após filtrar:' , X_train.shape)

# vizualiza os dados
# plt.hist(y_test, 50, facecolor='green')
# plt.show()


# faz o regressor
print('Treinando uma árvore de decisão otimizada com busca euxaustiva de '\
		'parâmetros...\n')
parameters = {'min_samples_split': [2, 5, 10, 15, 20, 25, 30],
				'max_depth': [15, 20, 25, 30, 35, 40, 50],
				'min_weight_fraction_leaf': [0.0, 0.3, 0.5]}
regr = grid_search.GridSearchCV(tree.DecisionTreeRegressor(), parameters)

# treinando o regressor
t0 = time()


regr = regr.fit(X_train, y_train)
best_parm = regr.best_params_
print("Resultados: \nTempo para treinar:", round(time()-t0, 3), "s")
print('Melhores parametros : %r' % best_parm)

# testando o regressor
test_regr(regr, X_test, y_test)


# treinando o regressor com boosting
print('Treinando a mesma árvore com adaptative boosting...\n')
par1 , par2 = best_parm['min_samples_split'], best_parm['max_depth']
regr = tree.DecisionTreeRegressor(min_samples_split = par1, max_depth = par2)
regr = AdaBoostRegressor(regr, n_estimators = 200)
regr = regr.fit(X_train, y_train)
print("Resultados: \nTempo para treinar:", round(time()-t0, 3), "s")


# testando o regressor
test_regr(regr, X_test, y_test)

print('--------------------------------------------------\n\n')