import pandas as pd
import numpy as np
from time import time
from sklearn.metrics import r2_score
from sklearn.decomposition import PCA


def test_regr(fit_regr, X_test, y_test, verbose = True):
	t0 = time()	
	s = ''
	
	pred = fit_regr.predict(X_test)
	s += "\nTempo para testar:" + str(round(time()-t0, 3)) + "s"

	r2 = r2_score(y_test, pred)
	s += '\nR^2 é: %.3f' % r2

	abs_err = np.abs(y_test - pred)
	s += '\nErro absoluto médio é: ± R$ %.2f' % np.mean(abs_err)
	s += '\nDesvio padrão do erro absoluto: %.2f' % np.std(abs_err)
	
	err_rel = np.abs((y_test - pred) / y_test) * 100
	s += '\nErro relativo médio é: %.2f' % np.mean(err_rel) + r'%'
	s += '\nDesvio padrão do erro relativo: %.3f\n' % np.std(err_rel)

	if verbose:
		print(s)

	return pred, abs_err, err_rel

def applyPCA(X_train, X_test, n_components, verbose = True):
	if verbose:
		print("Achando os top %d eigen-vectores" % n_components)

	t0 = time()
	s = '\nDimensões da matriz antes de aplicar PCA filtrar:'
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

