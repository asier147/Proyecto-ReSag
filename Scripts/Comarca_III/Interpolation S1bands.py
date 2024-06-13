
# -*- coding: utf-8 -*-
"""
Created on Sun May 19 11:07:04 2024

@author: Asier

Interpolation and filter of S-1 bands

"""

##Hay un duplicado en el el data frame de conservacion que se arrastra desde la descarga. Mirar en el shapefile si esta duplicada una misma parcela (dan valores distintos..)

import os
import pandas as pd
from scipy.signal import savgol_filter
import numpy as np




directory_path = "C:/Users/Asier/Desktop/Proyecto ReSAg/Archivos/Comarca_III/"
os.chdir(directory_path)

bandas_s1 = pd.read_csv("S1_III.csv")
bandas_s1=bandas_s1.rename(columns={'REFSIGPAC_min':'REFSIGPAC'})
bandas_s1=bandas_s1.rename(columns={'IDCOMARCA_min':'IDCOMARCA'})
################################################################################################################################################################

na_counts = bandas_s1.isna().sum()
print(na_counts)
bandas_s1.info()

bandas_s1 = bandas_s1.dropna()
bandas_s1 = bandas_s1[(bandas_s1 != 0).all(axis=1)]


bandas_s1['date']=bandas_s1['fecha']
################################################################################################################################################################

bandas = sorted([x for x in bandas_s1.columns.values if 'median' in x ])
columnas_fijas=['date','Manejo','REFSIGPAC']

bandas_s1 = bandas_s1.loc[:,columnas_fijas+bandas]
bandas_s1=bandas_s1.dropna()

bandas_s1['date'] = pd.to_datetime(bandas_s1['date'],format='%Y%m%d')
start_date = pd.to_datetime('2022-07-01')
end_date = pd.to_datetime('2023-06-30')   # Add one year for the end date
# Filter dataframe between start and end dates
bandas_23 = bandas_s1[(bandas_s1['date'] >= start_date) & (bandas_s1['date'] <= end_date)]

############################################################################################################################################

conservacion = bandas_23[bandas_s1['Manejo'] == 'Conservacion'].copy()
convencional = bandas_23[bandas_s1['Manejo'] == 'Convencional'].copy()
############################################################################################################################################

#Sacamos el número de parcelas por el SIGPAC en convencional
convencional_parcelas = convencional.drop_duplicates(subset=['REFSIGPAC'])
# Obtener los valores únicos de SIGPAC
convencional_parcelas = convencional_parcelas['REFSIGPAC'].tolist()
# Número de parcelas
len(convencional_parcelas)


#Sacamos el número de parcelas por el SIGPAC en conservacion
conservacion_parcelas = conservacion.drop_duplicates(subset=['REFSIGPAC'])
# Obtener los valores únicos de SIGPAC
conservacion_parcelas = conservacion_parcelas['REFSIGPAC'].tolist()

# Número de parcelas
len(conservacion_parcelas)
# Ponemos la fecha en un formato más fácil
conservacion['date'] = pd.to_datetime(conservacion['date']).dt.date
convencional['date'] = pd.to_datetime(convencional['date']).dt.date

############################################################################################################################################

df_por_parcela_convencional = {}
df_por_parcela_conservacion = {}

#Obtengo un dataframe con los valores de los indices y cada fecha para cada parcela

#Para parcelas convencional
for parcela_id in convencional_parcelas:
  # Filtrar por parcela
  df_parcela_conv = convencional.loc[convencional['REFSIGPAC'] == parcela_id]
  for fecha in df_parcela_conv['date']:
      for bandas in bandas:
          #Reiniciar el indice
          df_parcela_conv = df_parcela_conv.reset_index(drop=True)
          # Almacenar DataFrame en el diccionario
          df_por_parcela_convencional[parcela_id] = df_parcela_conv
   
          
#Para parcelas conservacion
for parcela_id in conservacion_parcelas:
  # Filtrar por parcela
  df_parcela_cons = conservacion.loc[conservacion['REFSIGPAC'] == parcela_id]
  for fecha in df_parcela_cons['date']:
      for banda in bandas:
          #Reiniciar el indice
          df_parcela_cons = df_parcela_cons.reset_index(drop=True)
          # Almacenar DataFrame en el diccionario
          df_por_parcela_conservacion[parcela_id] = df_parcela_cons

############################################################################################################################################
'''
def non_normal_outliers(data,col):
    IQR=data[col].quantile(0.75)-data[col].quantile(0.25)
    max_value=data[col].quantile(0.75) + (1.5*IQR)
    min_value=data[col].quantile(0.25) - (1.5*IQR)
    ab_sinout = data[col].between(min_value, max_value)
    df_sinout = data[ab_sinout]
    print(data.shape[0]-df_sinout.shape[0],'outliers eliminados para la variable',col)
    return df_sinout

sin_outliers_por_parcela_convencional = {}
for parcela_id, df_parcela in df_por_parcela_convencional.items():
    filtered_st_parcela_list = []
    for col in df_parcela.columns:
        if col not in['date','Manejo','Zona','Cultivo']:  # Excluir la columna 'date'
            filtered_st_parcela = non_normal_outliers(df_parcela, col)
            filtered_st_parcela_list.append(filtered_st_parcela)
    consolidated_df = pd.concat(filtered_st_parcela_list, ignore_index=True)
    sin_outliers_por_parcela_convencional[parcela_id] = consolidated_df
   
    
sin_outliers_por_parcela_conservacion = {}
for parcela_id, df_parcela in df_por_parcela_conservacion.items():
    filtered_st_parcela_list = []
    for col in df_parcela.columns:
        if col not in['date','Manejo','Zona','Cultivo']:  # Excluir la columna 'date'
            filtered_st_parcela = non_normal_outliers(df_parcela, col)
            filtered_st_parcela_list.append(filtered_st_parcela)
    consolidated_df = pd.concat(filtered_st_parcela_list, ignore_index=True)
    sin_outliers_por_parcela_conservacion[parcela_id] = consolidated_df
'''
############################################################################################################################################

def int_lineal(st_parcela):
    st_parcela=st_parcela.set_index('date')
    st_parcela.index= pd.to_datetime(st_parcela.index)

    # Generar una serie temporal diaria
    fecha_inicio = pd.Timestamp('2022-07-01')
    fecha_fin = pd.Timestamp('2023-06-30')
    indice = pd.date_range(start=fecha_inicio, end=fecha_fin, freq='D')
    df_int = pd.DataFrame(index=indice)
    df_int = pd.concat([df_int,st_parcela],axis=1)
    # dois = pd.Series([fecha.timetuple().tm_yday for fecha in st_parcela.index],index=st_parcela.index)
    manejo_value = st_parcela['Manejo'].iloc[0]
    ref_value = st_parcela['REFSIGPAC'].iloc[0]
    df_inter_dict={}
    for column in st_parcela.columns:
        if column not in['Manejo','REFSIGPAC']:
            st_parcela_int = df_int[column].interpolate(method='linear',limit_direction='both')
            df_inter_dict[column]=st_parcela_int
    manejo_series = pd.Series([manejo_value] * len(df_int), index=df_int.index, name='Manejo')
    ref_series=pd.Series([ref_value] * len(df_int), index=df_int.index, name='REFSIGPAC')
    df_inter = pd.concat(df_inter_dict.values(), axis=1)
    df_inter = pd.concat([manejo_series,ref_series,df_inter], axis=1)
    df_inter.reset_index(inplace=True)
    df_inter.rename(columns={'index': 'date'}, inplace=True)
    df_inter['date'] = df_inter['date'].dt.date
    return df_inter


sin_outliers__interpolacion_por_parcela_convencional = {}
for parcela_id, df_parcela in df_por_parcela_convencional.items():
    st_parcela = df_parcela.drop_duplicates(subset=['date']).iloc[:, [i for i, col in enumerate(df_parcela.columns) if 'median' in col  or 'date' in col or'Manejo' in col or 'REFSIGPAC' in col or 'Zona' in col or 'Cultivo' in col]]
    inter_st_parcela = int_lineal(st_parcela) 
    sin_outliers__interpolacion_por_parcela_convencional[parcela_id] = inter_st_parcela


sin_outliers__interpolacion_por_parcela_conservacion = {}
for parcela_id, df_parcela in df_por_parcela_conservacion.items():
    st_parcela = df_parcela.drop_duplicates(subset=['date']).iloc[:, [i for i, col in enumerate(df_parcela.columns) if 'median' in col  or 'date' in col or'Manejo' in col or 'REFSIGPAC' in col or 'Zona' in col or 'Cultivo' in col]]
    inter_st_parcela = int_lineal(st_parcela) 
    sin_outliers__interpolacion_por_parcela_conservacion[parcela_id] = inter_st_parcela


############################################################################################################################################
'''
def st_larga_savitzky_golay(st_parcela_int, oid):
    st_parcela_int=st_parcela_int.set_index('date')
    valores_m = range(11,80,5) # variar ventanas
    valores_d = range(2,5)
    results = pd.DataFrame(columns=['M','D','MSE'])
    best_mse = 10 # aleatorio numero inicial
    best_fit = None
    for column in st_parcela_int.columns:
        for m in valores_m:
            for d in valores_d:
                st_larga = savgol_filter(st_parcela_int[column], (2*m+ 1), d)
                # Calcular el error cuadrático medio (MSE)
                mse = np.median((st_parcela_int[column] - st_larga) ** 2)
                if mse <= best_mse:
                    best_mse = mse
                    best_fit = st_larga
                # Almacenar los resultados
                row = pd.DataFrame([[m,d,mse]],columns=['M','D','MSE'])
                results = pd.concat([results,row],axis=0, ignore_index=True)
        st_larga_best = pd.Series(best_fit, st_parcela_int.index)             
        best_comb = results.loc[results['MSE'].idxmin()]
        # Imprimir los resultados
        print("Mejor combinación de m y d:")
        print(best_comb)
    
    return st_larga_best


for parcela_id, df_parcela in sin_outliers__interpolacion_por_parcela_convencional.items():
    st_parcela_int=df_parcela.iloc[:, [i for i, col in enumerate(df_parcela.columns) if 'median' in col or 'Zona' in col or 'Cultivo' in col]]
    st_larga_best = st_larga_savitzky_golay(st_parcela_int,parcela_id)

for parcela_id, df_parcela in sin_outliers__interpolacion_por_parcela_conservacion.items():
    st_parcela_int=df_parcela.iloc[:, [i for i, col in enumerate(df_parcela.columns) if 'median' in col or 'Zona' in col or 'Cultivo' in col]]
    st_larga_best = st_larga_savitzky_golay(st_parcela_int,parcela_id)
    
#Mejor ventana 11, polinomio 4 o ventana 11 y polinomio 3
'''

############################################################################################################################################
##Para aplicar el filtro me quedo unicamente con los ya filtrados pero mantengo el dataframe con la original y la filtrada por si se quiere representar
bandas = sorted([x for x in convencional.columns.values if 'median' in x ])
selected_columns =['date','Manejo','REFSIGPAC']

df_limpio_convencional = {}
for parcela_id, df_parcela in sin_outliers__interpolacion_por_parcela_convencional.items():
    selected_columns_bandas = selected_columns.copy()
    # Vaciar la lista selected_columns
    selected_columns = ['date', 'Manejo', 'REFSIGPAC']    
    for banda in bandas:
        
        selected_columns_bandas.extend([banda])
        df_seleccionados = df_parcela[selected_columns_bandas]
        df_limpio_convencional[parcela_id] = df_seleccionados
        
df_limpio_conservacion = {}
for parcela_id, df_parcela in sin_outliers__interpolacion_por_parcela_conservacion.items():
    selected_columns_indices = selected_columns.copy()
    # Vaciar la lista selected_columns
    selected_columns = ['date', 'Manejo', 'REFSIGPAC']    
    for banda in bandas:
        
        selected_columns_indices.extend([banda])
        df_seleccionados = df_parcela[selected_columns_bandas]
        df_limpio_conservacion[parcela_id] = df_seleccionados     
        
############################################################################################################################################
'''
def st_filtro_savgol(df,indice):
    m_ = 5
    d = 3
    m = (2*m_+1)
    df[indice]=savgol_filter(df[indice],m, d)
    return df
    #df[f'{indice}std']=savgol_filter(df[f'{indice}_median'],m,d)

#Lo guardo en un nuevo diccionario por si acaso para poder ver comparativas si hiciese falta
df_savgol_convencional = {}
for parcela_id, df_parcela in df_limpio_convencional.items():    
    for banda in bandas:
        df_filtrado = st_filtro_savgol(df_parcela,banda)
    df_savgol_convencional[parcela_id] = df_filtrado
    
df_savgol_conservacion = {}
for parcela_id, df_parcela in df_limpio_conservacion.items():    
    for banda in bandas:
        df_filtrado = st_filtro_savgol(df_parcela,banda)
    df_savgol_conservacion[parcela_id] = df_filtrado
'''    
############################################################################################################################################
#Unimos los datos y los guardamos

df_bandas_convencional = pd.concat(df_limpio_convencional.values(), ignore_index=True)
df_bandas_conservacion = pd.concat(df_limpio_conservacion.values(), ignore_index=True)
#Lo guardamos a un csv
guardado_path = "C:/Users/Asier/Desktop/Proyecto ReSAg/Archivos/Comarca_III"
os.chdir(guardado_path)
df_bandas_convencional.to_csv('convencional_S1_bandas_filtrado_III.csv', index=False)

df_bandas_conservacion.to_csv('conservacion_S1_bandas_filtrado_III.csv', index=False)
