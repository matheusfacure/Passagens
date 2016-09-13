import sys
from time import time
sys.path.append("./tools/")
import datetime as dt
import re
from pprint import pprint as pp
import numpy as np
import pandas as pd
import pandasql
from sklearn.cross_validation import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn import tree, grid_search
from sklearn.ensemble import AdaBoostRegressor

from process_skyscanner import load_CSVs

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



# lida com NaNs
for var in df.columns:
	n_nans = sum(pd.isnull(df[var]))
	if n_nans > 0:
		print("Variável %s tem %d NaNs" % (var, n_nans))

print('\nSubstituindo os NaNs por %d...' % 0)
df = df.fillna(0)
print("Tempo para filtrar os dados:", round(time()-t0, 3), "s\n")
print("Dimensões da matriz filtrada: ", df.shape, '\n')

train, test = train_test_split(df, test_size = 0.2)
y_train, y_test = train['preco'], test['preco']
X_train, X_test = train.drop('preco', 1), test.drop('preco', 1)


# faz o regressor
print('Treinando uma decision tree otimizada com GridSearchCV()...')
parameters = {'min_samples_split': [2, 5, 10, 15, 20, 25, 30],
				'max_depth': [15, 20, 25, 30, 35, 40, 50]}
regr = grid_search.GridSearchCV(tree.DecisionTreeRegressor(), parameters)

# treinando o regressor
t0 = time()
regr = regr.fit(X_train, y_train)
best_parm = regr.best_params_
print("Resultados: \nTempo para treinar:", round(time()-t0, 3), "s")
print('Melhores parametros : %r' % best_parm)

# testando o regressor
t0 = time()	
pred = regr.predict(X_test)
print("Tempo para testar:", round(time()-t0, 3), "s")

r2 = r2_score(y_test, pred)
print('R² é: ', r2)

me_abs_err = mean_absolute_error(y_test, pred)
print('Erro absoluto médio é: ± R$ %.2f \n\n' % round(me_abs_err, 2))



# treinando o regressor com boosting
print('Treinando a mesma decision tree com Ada Boosting...')
par1 , par2 = best_parm['min_samples_split'], best_parm['max_depth']
regr = tree.DecisionTreeRegressor(min_samples_split = par1, max_depth = par2)
regr = AdaBoostRegressor(regr, n_estimators = 300)
regr = regr.fit(X_train, y_train)
print("Resultados: \nTempo para treinar:", round(time()-t0, 3), "s")


# testando o regressor
t0 = time()	
pred = regr.predict(X_test)
print("Tempo para testar:", round(time()-t0, 3), "s")

r2 = r2_score(y_test, pred)
print('R² é: ', r2)

me_abs_err = mean_absolute_error(y_test, pred)
print('Erro absoluto médio é: ± R$ %2f \n\n' % round(me_abs_err, 2))
print('-------------------------------------------------------------\n\n\n')