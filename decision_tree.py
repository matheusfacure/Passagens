import sys
from time import time
sys.path.append("./tools/")
import datetime as dt
import re
from pprint import pprint as pp
import pandasql
from sklearn.cross_validation import train_test_split
from sklearn.metrics import r2_score
from sklearn import tree, grid_search

from process_skyscanner import load_CSVs


df = load_CSVs('./tools/BSB-VCP*.csv')

# pp(df.columns.to_series().groupby(df.dtypes).groups)

# targets

# query df
q = """
SELECT preco, col_wday, col_hour, col_yday, out_stop1, in_stop1, 
 agent, out_orStat, out_desStat
FROM df
"""

df = pandasql.sqldf(q.lower(), locals())

train, test = train_test_split(df, test_size = 0.2)
y_train, y_test = train['preco'], test['preco']
X_train, X_test = train.drop('preco', 1), test.drop('preco', 1)


# make regressor
parameters = {'min_samples_split': [3, 5, 10, 11],
				'max_depth': [3, 5, 9, 15]}
regr = grid_search.GridSearchCV(tree.DecisionTreeRegressor(), parameters)


# treinando o regressor
t0 = time()
regr = regr.fit(X_train, y_train)
print("Tempo para treinar:", round(time()-t0, 3), "s")

# testando o regressor
t0 = time()	
pred = clf.predict(X_train)
print("Tempo para testar:", round(time()-t0, 3), "s")

r2 = r2_score(y_test, pred)
print('R² é: ', r2_score)