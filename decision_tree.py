import sys
from time import time
sys.path.append("./tools/")
import datetime as dt
import re
from pprint import pprint as pp
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
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

	return pred, abs_err, err_rel


# carrega os arquvios
t0 = time()

var_list= ['preco', 'col_wday', 'col_hour', 'col_yday', 'out_stop1', 'in_stop1', 
 'agent', 'out_orStat', 'out_desStat', 'ag_type', 'in_carr1', 'out_carr1',
 'out_chegada', 'out_saida', 'in_saida', 'in_chegada']

path = '/media/matheus/EC2604622604305E/data/Passagens/CSV_Format/BSB-VCP*.csv'
df = load_CSVs(path, var_list, max_files = 2)
print("Tempo para carregar os dados:", round(time()-t0, 3), "s\n")
# pp(df.columns.to_series().groupby(df.dtypes).groups)
	

# Filtra a df apenas com as variáveis selecionadas
t0 = time()



# novas variáveis

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

# lida com NaNs
for var in df.columns:
	n_nans = sum(pd.isnull(df[var]))

df = df.fillna(0)

print("Dimensões da matriz: ", df.shape, '\n')

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


print('Tempo para filtrar os dados:', round(time()-t0, 3), 's\n')
print('Dimensões da matriz após filtrar:' , X_train.shape)


# faz o regressor
print('\nTreinando uma árvore de decisão otimizada com busca euxaustiva de '\
		'parâmetros...\n')
parameters = {'min_samples_split': [5, 10, 15, 20, 25, 30],
				'max_depth': [20, 25, 30, 35, 45]}
regr = grid_search.GridSearchCV(tree.DecisionTreeRegressor(), parameters)

# treinando o regressor
regr = regr.fit(X_train, y_train)
best_parm = regr.best_params_
print("Resultados: \nTempo para treinar:", round(time()-t0, 3), "s")
print('Melhores parametros : %r' % best_parm)

# testando o regressor
pred, abs_err, err_rel = test_regr(regr, X_test, y_test)
