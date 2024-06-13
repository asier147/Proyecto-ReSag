# -*- coding: utf-8 -*-
"""
Random Forest 

- A partir de: 70% datos en el conjunto de entrenamiento (valor CE, se puede modificar)

@author: Asier Herrera
"""
import datetime
from sklearn import metrics, model_selection
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import pandas as pd
import os
#Definición de variables constantes:
CE = 0.70
#Definición de funciones:
def RF(X,y,CE):
    ##SEPARAR DATOS DE CALIBRACIÓN DE MODELO Y TEST MEDIANTE VALIDACIÓN CRUZADA:
    # np.random.seed(12) #Se fija la semilla de numpy para que la generación aleatoria siempre nos de los mismos números
    X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, train_size=CE, random_state=12)
    '''
    CALIBRAR EL MODELO PARA ELEGIR LOS MEJORES PARÁMETROS CON DATOS DE CALIBRACIÓN.
    Los parámetros de entrada son:
        criterion: tipo de medida de impureza ('gini' o 'entropy'). Por defecto es gini.
        max_features: número de variables a evaluar en cada nodo de cada árbol de decisión que forma en random forest. Los valores que puede tomar son:
            'auto': hace la raíz cuadrada del número de variables (valor por defecto).
            'sqrt': hace la raíz cuadrada del número de variables.
            'log2': hace el logaritmo en base dos del número de variables.
        n_estimators: valor entero que determina el número de clasificadores que compondrán el ensemble. Por defecto es 10.
        max_depth: profundidad máxima permitida al construir cada árbol de decisión base.
        min_samples_split: número mínimo de ejemplos necesarios para dividir un nodo.
        random_state: valor que determina la semilla para la generación de números aleatorios.
    '''
    print('Ajustando mejores parámetros',print(datetime.datetime.now()))
    RF = RandomForestClassifier() 
    param_grid = {'n_estimators': [10,50,100], 'max_features': ['sqrt','log2',None], 'criterion': ['gini','entropy'], 'max_depth': [5,10,None], 'min_samples_split': [2,10,20]}

    #Llamada la función GridSearchCV que nos crea todas las cominaciones del grid anterior
    clasificadoresRF = model_selection.GridSearchCV(RF, param_grid, scoring='accuracy', cv=5,n_jobs=-1,verbose = 3)
    clasificadoresRF = clasificadoresRF.fit(X_train, y_train)
    # Se muestra la mejor configuración y su accuracy asociado
    print(clasificadoresRF.best_params_)
    print(clasificadoresRF.best_score_)
    '''
    ENTRENAR EL MODELO CON DATOS DE CALIBRACIÓN Y MEDIR EL ACCURACY CON LOS DATOS TEST (con los parámetros del punto anterior)
    '''
    # LLamada al constructor del random forest utilizando los parámetros del punto anterior
    bestparams = clasificadoresRF.best_params_
    RF = RandomForestClassifier(criterion = bestparams['criterion'], 
                                max_depth = bestparams['max_depth'], 
                                max_features = bestparams['max_features'], 
                                min_samples_split = bestparams['min_samples_split'], 
                                n_estimators = bestparams['n_estimators'])
    
    print('Entrenando el modelo')
    # Entrenamiento del árbol de decisión
    RF.fit(X_train, y_train)
    # Se realizan las predicciones del árbol de decisión con los ejemplos de entrenamiento
    predictionTrain = RF.predict(X_train)
    # Se obtiene el rendimiento (accuracy)
    accTrain = metrics.accuracy_score(y_train, predictionTrain)*100.0
    # Predicción de los datos de test
    predictionTest = RF.predict(X_test)
    # Cálculo del porcentaje de acierto en test (entre 0.0 y 100.0)
    accTest = metrics.accuracy_score(y_test, predictionTest)*100.0
    # Se imprime la información de los rendimientos
    print("Train: {}, test: {}".format(accTrain, accTest))
    return bestparams,predictionTrain,accTrain,predictionTest,accTest
'''
CARGA DE DATAFRAME CON TODOS LOS DATOS
'''
########################################################################################################################
directory_path = r"D:\MASTER2324\00-TFM\HerreraAsier\00-parcelas\wetransfer_ficheros_2024-05-30_1533"

# Change the current working directory
os.chdir(directory_path)

grouped = pd.read_csv('fich_RF.csv',index_col=0)
########################################################################################################################
#Opción de serie temporal completa
########################################################################################################################

colsx = [x for x in grouped.columns if x not in ['Manejo']]

X = np.array(grouped[colsx])
y = np.array(grouped['Manejo'])
cols,bp,pTR,aTR,pTS,aTS = [],[],[],[],[],[]
#################################
#####  ####
#################################
columnasx = [x for x in grouped.columns]
best_params, pTrain, aTrain, pTest,aTest = RF(X,y, CE = CE)
cols.append(columnasx),bp.append(best_params),pTR.append(pTrain),aTR.append(aTrain),pTS.append(pTest),aTS.append(aTest)#################################
