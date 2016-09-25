import sys
from time import time
sys.path.append("./tools/")
from pprint import pprint as pp
import numpy as np
import pandas as pd
from sklearn.svm import SVR
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import BaggingRegressor, AdaBoostRegressor
from process_skyscanner import load_CSVs, data_split
from tranfs_train_test import test_regr, applyPCA, remove_outliers, applyICA
np.random.seed(123)



# carrega os arquvios
t0 = time()

var_list= ['preco', 'col_wday', 'col_hour', 'col_yday', 'out_stop1', 'in_stop1', 
 'agent', 'out_orStat', 'out_desStat', 'ag_type', 'in_carr1', 'out_carr1',
 'out_chegada', 'out_saida', 'in_saida', 'in_chegada']

path = '/media/matheus/EC2604622604305E/data/Passagens/CSV_Format/BSB-VCP*.csv'
df = load_CSVs(path, var_list, max_files = 10, n_days = 3)
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

# lidando com n_nans
for var in df.columns:
	n_nans = sum(pd.isnull(df[var]))

df = df.fillna(0)


#train, test = data_split(df, shuffle = True, test_stize = 0.2)
train, test = data_split(df, shuffle = False)
y_train, y_test = train['preco'], test['preco']
X_train, X_test = train.drop('preco', 1), test.drop('preco', 1)


# lindando com outliers
X_train, y_train = remove_outliers(X_train, y_train, n_std = 3, verbose = False)

print('Tempo para filtrar os dados:', round(time()-t0, 3), 's\n')
print('Dimensões da matriz após filtrar:' , X_train.shape)


#X_train = X_train.head(1000)
#y_train = y_train.head(1000)

# scaling 
scaler = MinMaxScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.fit_transform(X_test)

# PCA
X_train, X_test = applyPCA(X_train, X_test, 40)

# fazendo o regressor
t0 = time()

regr = SVR(kernel='rbf', gamma = 0.01, C = 100, cache_size = 1000)
#regr = SVR(kernel='poly', degree = 3, C = 50, cache_size = 500)

#regr = BaggingRegressor(regr, max_samples = 0.8, n_estimators = 4,
#						bootstrap = False, n_jobs = -1)
regr = AdaBoostRegressor(regr, n_estimators = 50)



print('Treinando o SVR')
t0 = time()
regr = regr.fit(X_train, y_train)
print("Resultados: \nTempo para treinar:", round(time()-t0, 3), "s")

test_regr(regr, X_test, y_test)

