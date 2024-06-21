# -*- coding: utf-8 -*-
"""
Random Forest - Muestras equilibradas
- A partir de: 70% datos en el conjunto de entrenamiento (valor CE, se puede modificar)

@author: ASIER HERRERA
"""
from sklearn import model_selection
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.metrics import recall_score
from sklearn.metrics import precision_score
from sklearn.metrics import f1_score
from imblearn.over_sampling import SMOTE
from imblearn.metrics import geometric_mean_score
import numpy as np
import pandas as pd
import errno
import os
import sys
import glob
import joblib


#########################
#Definición de variables constantes:

CE = 0.70
#########################
#Definición de funciones:
def create_dir(ruta):
    try: os.makedirs(ruta)
    except OSError as e:
        if e.errno != errno.EEXIST: raise
        
def RF(df,CE, bandas):
    global dftrain,dftest, dfCM, dfm
    #Creamos una columna xy que servirá como identificador:
    colsx = [x for x in df.columns if x not in ['Manejo']]
    X = np.array(df[colsx])
    y = np.array(df['Manejo'])
    ##SEPARAR DATOS DE CALIBRACIÓN DE MODELO Y TEST MEDIANTE VALIDACIÓN CRUZADA:
    print('Hold-out...')
    np.random.seed(12) #Se fija la semilla de numpy para que la generación aleatoria siempre nos de los mismos números
    X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, train_size=CE, random_state=12)
    dftr, dftt = pd.DataFrame(X_train),pd.DataFrame(X_test)
    dftr.columns = dftt.columns = colsx

    ##MUESTREO PARA REALIZAR UNA CLASIFICACIÓN BALANCEADA:
    #print('Realizando muestreo SMOTE',tiempo())
   #Muestras sinteticas smote = SMOTE(random_state=12)
   # X_sm, y_sm = smote.fit_resample(X_train,y_train)
    print('Muestreo acabado')
    dftest=dftt

    # LLamada al constructor del random forest utilizando los parámetros del punto anterior
    RF = RandomForestClassifier(criterion = 'gini', 
                                max_depth = None, 
                                max_features = 'log2', 
                                min_samples_split = 2, 
                                n_estimators = 100)
    print('Entrenando el modelo...', )
    # Entrenamiento del árbol de decisión
    RF.fit(X_train, y_train)
    # print('Modelo entrenado. Guardando modelo...',tiempo())
    # print(os.path.join(dirfin,'RF_'+bandas+'_'+nivel+'.joblib'))
    # joblib.dump(RF,os.path.join(dirfin,'RF_'+bandas+'_'+nivel+'.joblib'), compress = 3)
    # print('Modelo guardado',tiempo())
    # Se realizan las predicciones del árbol de decisión con los ejemplos de entrenamiento
    print('Clasificando...', )
    y_ptrain = RF.predict(X_train)
    # Predicción de los datos de test
    y_ptest = RF.predict(X_test)
    # Confusion Matrix
    CM = confusion_matrix(y_test, y_ptest)
    # Accuracy
    accTest = accuracy_score(y_test, y_ptest)
    accTrain = accuracy_score(y_train, y_ptrain)
    # Recall
    RS = recall_score(y_test, y_ptest, average=None)
    # Precision
    PS = precision_score(y_test, y_ptest, average=None)
    #F1
    F1 = f1_score(y_test, y_ptest, average=None)
    F1b = f1_score(y_test, y_ptest, average='weighted')
    #Geometric median score:
    gmc = geometric_mean_score(y_test,y_ptest, average = 'weighted')
    dfm = pd.DataFrame(list(zip(RS,PS,F1)),columns =['Recall', 'Precision','F1'])
    dfm['Accuracy_Train'] = np.nan
    dfm['Accuracy_Test'] = np.nan
    dfm['F1_weighted'] = np.nan
    dfm['GM_weighted'] = np.nan
    dfm = dfm.T
    dfm.columns = list(set(y))
    dfm['Total'] = np.nan
    dfm['Total']['Accuracy_Train'] = accTrain
    dfm['Total']['Accuracy_Test'] = accTest
    dfm['Total']['F1_weighted'] = F1b
    dfm['Total']['GM_weighted'] = gmc
    dftrain = pd.DataFrame(y_train)
    dftrain = pd.concat([dftrain,pd.DataFrame(y_ptrain)], axis = 1)
    dftrain.columns = ['y_train','Pred_train']
    #dftrain.insert(dftrain.shape[1], "y_train", y_train)
    #dftrain.insert(dftrain.shape[1], "Pred_train", y_ptrain)
    dftest.insert(dftest.shape[1], "y_test", y_test)
    dftest.insert(dftest.shape[1], "Pred_test", y_ptest)
    dfCM = pd.DataFrame(CM)
    dfCM.index = dfCM.columns = list(set(y))

    dftrain.to_excel(os.path.join(dirfin,bandas+'_Pred_train_'+'_'+'.xlsx'))#poner nombre que yo quiera

    dftest.to_excel(os.path.join(dirfin,bandas+'_Pred_test_'+'_'+'.xlsx'))#poner nombre que yo quiera
    dfCM.to_excel(os.path.join(dirfin,bandas+'_MConfusion_'+'_'+'.xlsx'))#poner nombre que yo quiera
    dfm.to_excel(os.path.join(dirfin,bandas+'_Metricas_'+'_'+'.xlsx'))#poner nombre que yo quiera

    print('Calculando variables de importancia...')
    
    #########################
    #IMPORTANCIA DE VARIABLES
    #########################
    #Random Forest Built-in Feature Importance: Gini importance (or median decrease impurity)
    gini_importance = RF.feature_importances_ #MDG (MDI)
    dfguradar = pd.DataFrame(zip(colsx,gini_importance), columns = ['variable','MDG']).sort_values(by = 'MDG', ascending = False)
    dfguradar.to_excel(os.path.join(dirfin,bandas+'_MDG_'+'.xlsx'))#poner nombre que yo quiera
    
    print('Leyendo dfmix...')

directory_path = "C:/Users/Asier/Desktop/Proyecto ReSAg/Archivos/"

# Change the current working directory
os.chdir(directory_path)

dfmix = pd.read_csv('fich_RF_total.csv',index_col=0)


indices = [x for x in dfmix.columns if 'DFI_median'in x or'NDSVI_median'in x or'NDTI_median' in x] #columnas indices opticos
bandas = [x for x in dfmix.columns if 'B3_median' in x or 'B8_median'in x or'B12_median' in x] #columnas bandas
S1 = [x for x in dfmix.columns if 'median_B2'in x or'median_B3'in x or'median_B4' in x]
combs = [indices,S1,indices+S1,bandas,indices+bandas,S1+bandas,indices+S1+bandas]
bandass = ['indices','S1','indices-S1','bandas','indices-bandas','S1-bandas','indices-S1-bandas']

for comb, bandas in zip(combs, bandass):
    print(bandas)    
    df_i = dfmix[['Manejo']+comb]
    ordencols = pd.DataFrame(dfmix.columns)
                    
    dirfin  = os.path.join("C:/Users/Asier/Desktop/Proyecto ReSAg/Archivos/RF_total",bandas)
    create_dir(dirfin)
    print(dirfin)
    ordencols.to_excel(os.path.join(dirfin,'OrdenColumnasRF_'+'.xlsx'))
    print('Realizando clasificación')
    # dfnivel = dfmix[[nivel]+[x for x in dfmix if x not in niveles]]
    RF(df_i,CE = CE,bandas = bandas)
            
    
       

