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
from sklearn.metrics import r2_score
from sklearn import tree, grid_search

from process_skyscanner import load_CSVs

# carrega os arquvios
t0 = time()
path = '/media/matheus/EC2604622604305E/data/Passagens/CSV_Format/BSB-VCP*.csv'
df = load_CSVs(path, 5)
print("Tempo para carregar os dados:", round(time()-t0, 3), "s")
	

# Filtra a df apenas com as variáveis selecionadas
t0 = time()

q = """
SELECT preco, col_wday, col_hour, col_yday, out_stop1, in_stop1, 
 agent, out_orStat, out_desStat
FROM df
"""
df = pandasql.sqldf(q.lower(), locals())


# lida com NaNs
df = df.fillna(0)
print("Tempo para filtrar os dados:", round(time()-t0, 3), "s")


train, test = train_test_split(df, test_size = 0.2)
y_train, y_test = train['preco'], test['preco']
X_train, X_test = train.drop('preco', 1), test.drop('preco', 1)



# faz o regressor
parameters = {'min_samples_split': [5, 10, 15, 20],
				'max_depth': [15, 20, 35]}
regr = grid_search.GridSearchCV(tree.DecisionTreeRegressor(), parameters)


# treinando o regressor
t0 = time()
regr = regr.fit(X_train, y_train)
print("Tempo para treinar:", round(time()-t0, 3), "s")
print('Melhores parametros : %r' % regr.best_params_)

# testando o regressor
t0 = time()	
pred = regr.predict(X_test)
print("Tempo para testar:", round(time()-t0, 3), "s")

r2 = r2_score(y_test, pred)
print('R² é: ', r2)