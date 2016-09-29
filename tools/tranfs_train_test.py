import pandas as pd
import numpy as np
from time import time, localtime, strftime
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.decomposition import PCA, FastICA
from sklearn.grid_search import ParameterGrid


def test_regr(fit_regr, X_train, y_train, X_test, y_test,
			verbose = True, keep_log = False):
	t0 = time()	
	s = '\n'
	pred = fit_regr.predict(X_test)
	pred_train = fit_regr.predict(X_train)
	s += "\nTempo para testar:" + str(round(time()-t0, 3)) + "s"
	s += '\nParametros: \n' + str(fit_regr.get_params()) + '\n'
	for w, p, y, x in zip(['Treino', 'Teste'], [pred_train, pred],
						[y_train, y_test], [X_train, X_test]):
		s += '\n---------------------------------------------'
		s += '\nNo set de %s :' % w
		s += '\nDimenção dos imputs é ' + str(x.shape)
		r2 = r2_score(y, p)
		s += '\nR^2 é: %.3f' % r2

		abs_err = np.abs(y - p)
		s += '\nErro absoluto médio é: ± R$ %.2f' % np.mean(abs_err)
		s += '\nDesvio padrão do erro absoluto: %.2f' % np.std(abs_err)
		
		err_rel = np.abs((y - p) / y) * 100
		s += '\nErro relativo médio é: %.2f' % np.mean(err_rel) + r'%'
		s += '\nDesvio padrão do erro relativo: %.3f\n' % np.std(err_rel)

	if verbose:
		print(s)
	
	if keep_log:
		with open('relatorio.txt', 'a') as relatorio:
			relatorio.write('#############################################\n')
			relatorio.write(strftime('%Y-%m-%d %H:%M', localtime()))
			relatorio.write(s)
			relatorio.write('#############################################\n\n')
		
	return pred, abs_err, err_rel


def days_cv(X_train, y_train, X_test, y_test):
	for day in X_test.col_yday.unique():
		slvect = X_test['col_yday'] == day
		test_regr(regr, X_train, y_train, X_test[slvect], y_test[slvect])


def applyPCA(X_train, X_test, n_components, verbose = False):
	if verbose:
		print("\n\nAchando os top %d eigen-vectores" % n_components)

	t0 = time()
	s = '\nDimensões da matriz antes de aplicar PCA:'
	s += str(X_train.shape)

	pca = PCA( n_components = n_components)
	
	pca.fit(X_train)
	X_train = pca.transform(X_train)
	X_test = pca.transform(X_test)
	s += '\nTop 5 componentes principais: '
	s += str(pca.explained_variance_ratio_[:5]) 
	s += "\nFeito em %0.3fs" % (time() - t0)
	s += '\nDimensões da matriz após aplicas PCA:' + str(X_train.shape)
	if verbose:
		print(s)
	return X_train, X_test 

def applyICA(X_train, X_test, n_components, max_iter, verbose = True):
	if verbose:
		print("\n\nAplicando ICA com %d componetes" % n_components)
	
	s = '\nDimensões da matriz antes de aplicar ICA:'
	t0 = time()
	ica = FastICA(n_components=n_components, max_iter = max_iter)
	
	ica.fit(X_train)
	X_train = ica.transform(X_train)
	X_test = ica.transform(X_test)
	s += "\nFeito em %0.3fs" % (time() - t0)
	s += '\nDimensões da matriz após aplicas ICA:' + str(X_train.shape)
	if verbose:
		print(s)
	return X_train, X_test 


def remove_outliers(X_train, y_train, n_std = 3, verbose = False):

	top_outliers = y_train > np.mean(y_train) + n_std * np.std(y_train)
	botom_outliers = y_train < np.mean(y_train) - n_std * np.std(y_train)
	
	tot_outliers = np.logical_not(np.logical_or(botom_outliers, top_outliers))
	

	s = '\n\nTemos %d outliers no topo' % sum(top_outliers)
	s += '\nIsso equivale à %.3f' % (sum(top_outliers) / len(y_train)) + r'%'
	s += '\nTemos %d outliers na base' % sum(botom_outliers)
	s += '\nIsso equivale à %.3f' % (sum(botom_outliers) / len(y_train)) + r'%'
	if verbose:
		print(s)

	y_train = y_train[tot_outliers]
	X_train = X_train[tot_outliers]

	return X_train, y_train



