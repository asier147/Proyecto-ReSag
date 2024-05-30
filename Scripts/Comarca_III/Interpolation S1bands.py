# -*- coding: utf-8 -*-
"""
Created on Thu May 30 18:37:24 2024

@author: Asier
Interpoltation S-1 bands
"""


import os
import pandas as pd
from scipy.signal import savgol_filter
import numpy as np




directory_path = "C:/Users/Asier/Desktop/Proyecto ReSAg/Archivos/Comarca_III/"
os.chdir(directory_path)

bandas_s1 = pd.read_csv("S1_ASC_103_III.csv")

################################################################################################################################################################

na_counts = bandas_s1.isna().sum()
print(na_counts)
bandas_s1.info()

bandas_s1 = bandas_s1.dropna()
bandas_s1 = bandas_s1[(bandas_s1 != 0).all(axis=1)]


bandas_s1['date']=bandas_s1['fecha']
################################################################################################################################################################

bandas = sorted([x for x in bandas_s1.columns.values if 'mean' in x ])
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

# Get the number of parcels by SIGPAC in conventional management
convencional_parcelas = convencional.drop_duplicates(subset=['REFSIGPAC'])
# Get unique SIGPAC values
convencional_parcelas = convencional_parcelas['REFSIGPAC'].tolist()
# Number of plots
len(convencional_parcelas)


# Get the number of plots by SIGPAC in conservation managementn
conservacion_parcelas = conservacion.drop_duplicates(subset=['REFSIGPAC'])
# Get unique SIGPAC values
conservacion_parcelas = conservacion_parcelas['REFSIGPAC'].tolist()

# Number of parcels
len(conservacion_parcelas)
# Convert the date to an easier format
conservacion['date'] = pd.to_datetime(conservacion['date']).dt.date
convencional['date'] = pd.to_datetime(convencional['date']).dt.date

############################################################################################################################################


df_por_parcela_convencional = {}
df_por_parcela_conservacion = {}

# Create a dataframe with index values and each date for each parcel

# For conventional parcels
for parcela_id in convencional_parcelas:
# Filter by parcel
  df_parcela_conv = convencional.loc[convencional['REFSIGPAC'] == parcela_id]
  for fecha in df_parcela_conv['date']:
      for bandas in bandas:
          # Reset the index
          df_parcela_conv = df_parcela_conv.reset_index(drop=True)
          # Store DataFrame in the dictionary
          df_por_parcela_convencional[parcela_id] = df_parcela_conv
   
          
# For conservation parcels
for parcela_id in conservacion_parcelas:
# Filter by parcel
  df_parcela_cons = conservacion.loc[conservacion['REFSIGPAC'] == parcela_id]
  for fecha in df_parcela_cons['date']:
      for banda in bandas:
          # Reset the index
          df_parcela_cons = df_parcela_cons.reset_index(drop=True)
          # Store DataFrame in the dictionary
          df_por_parcela_conservacion[parcela_id] = df_parcela_cons

############################################################################################################################################

 # Function to remove outliers from a dataset based on interquartile range (IQR)             
def non_normal_outliers(data,col):
    IQR=data[col].quantile(0.75)-data[col].quantile(0.25)
    max_value=data[col].quantile(0.75) + (1.5*IQR)
    min_value=data[col].quantile(0.25) - (1.5*IQR)
    ab_sinout = data[col].between(min_value, max_value)
    df_sinout = data[ab_sinout]
    print(data.shape[0]-df_sinout.shape[0],'outliers eliminados para la variable',col)
    return df_sinout


# Dictionary to store cleaned data for conventional parcels
sin_outliers_por_parcela_convencional = {}
# Loop over conventional parcel IDs and their respective dataframes
for parcela_id, df_parcela in df_por_parcela_convencional.items():
    filtered_st_parcela_list = []
    # Iterate over columns in the dataframe, excluding specific ones
    for col in df_parcela.columns:
        if col not in['date','Manejo','REFSIGPAC','Cultivo']:  
            # Remove outliers for the column and store the cleaned dataframe
            filtered_st_parcela = non_normal_outliers(df_parcela, col)
            filtered_st_parcela_list.append(filtered_st_parcela)
    # Concatenate the cleaned dataframes and store them in the dictionary
    consolidated_df = pd.concat(filtered_st_parcela_list, ignore_index=True)
    sin_outliers_por_parcela_convencional[parcela_id] = consolidated_df
   
# Dictionary to store cleaned data for conservation parcels    
sin_outliers_por_parcela_conservacion = {}
# Loop over conservation parcel IDs and their respective dataframes
for parcela_id, df_parcela in df_por_parcela_conservacion.items():
    filtered_st_parcela_list = []
    # Iterate over columns in the dataframe, excluding specific ones
    for col in df_parcela.columns:
        if col not in['date','Manejo','REFSIGPAC','Cultivo']:
            # Remove outliers for the column and store the cleaned dataframe
            filtered_st_parcela = non_normal_outliers(df_parcela, col)
            filtered_st_parcela_list.append(filtered_st_parcela)
    # Concatenate the cleaned dataframes and store them in the dictionary
    consolidated_df = pd.concat(filtered_st_parcela_list, ignore_index=True)
    sin_outliers_por_parcela_conservacion[parcela_id] = consolidated_df
    
############################################################################################################################################

def int_lineal(st_parcela):
    st_parcela=st_parcela.set_index('date')
    st_parcela.index= pd.to_datetime(st_parcela.index)

    # Generate a daily time series
    fecha_inicio = pd.Timestamp('2022-07-01')
    fecha_fin = pd.Timestamp('2023-06-30')
    indice = pd.date_range(start=fecha_inicio, end=fecha_fin, freq='D')
    df_int = pd.DataFrame(index=indice)
    df_int = pd.concat([df_int,st_parcela],axis=1)
    manejo_value = st_parcela['Manejo'].iloc[0]
    ref_value = st_parcela['REFSIGPAC'].iloc[0]
    cultivo_value = st_parcela['Cultivo'].iloc[0]
    df_inter_dict={}
    for column in st_parcela.columns:
        if col not in['Manejo','Cultivo','REFSIGPAC']:
            st_parcela_int = df_int[column].interpolate(method='linear',limit_direction='both')
            df_inter_dict[column]=st_parcela_int
    manejo_series = pd.Series([manejo_value] * len(df_int), index=df_int.index, name='Manejo')
    ref_series=pd.Series([ref_value] * len(df_int), index=df_int.index, name='REFSIGPAC')
    cultivo_series=pd.Series([cultivo_value] * len(df_int), index=df_int.index, name='Cultivo')
    df_inter = pd.concat(df_inter_dict.values(), axis=1)
    df_inter = df_inter.drop(['Manejo','REFSIGPAC','Cultivo'], axis=1)
    df_inter = pd.concat([manejo_series,ref_series,cultivo_series,df_inter], axis=1)
    df_inter.reset_index(inplace=True)
    df_inter.rename(columns={'index': 'date'}, inplace=True)
    df_inter['date'] = df_inter['date'].dt.date
    return df_inter
# Dictionary to store data with linear interpolation for conventional parcels
sin_outliers__interpolacion_por_parcela_convencional = {}
# Loop over conventional parcel IDs and their respective dataframes
for parcela_id, df_parcela in sin_outliers_por_parcela_convencional.items():
    st_parcela = df_parcela.drop_duplicates(subset=['date']).iloc[:, [i for i, col in enumerate(df_parcela.columns) if 'mean' in col  or 'date' in col or'Manejo' in col or 'REFSIGPAC' in col or 'Cultivo' in col]]
    inter_st_parcela = int_lineal(st_parcela) 
    sin_outliers__interpolacion_por_parcela_convencional[parcela_id] = inter_st_parcela

# Dictionary to store data with linear interpolation for conservation parcels
sin_outliers__interpolacion_por_parcela_conservacion = {}
# Loop over conservation parcel IDs and their respective dataframes
for parcela_id, df_parcela in sin_outliers_por_parcela_conservacion.items():
    st_parcela = df_parcela.drop_duplicates(subset=['date']).iloc[:, [i for i, col in enumerate(df_parcela.columns) if 'mean' in col  or 'date' in col or'Manejo' in col or 'REFSIGPAC' in col  or 'Cultivo' in col]]
    inter_st_parcela = int_lineal(st_parcela) 
    sin_outliers__interpolacion_por_parcela_conservacion[parcela_id] = inter_st_parcela

############################################################################################################################################
# Function to select Savitzky-Golay filter for long-term smoothing
def st_larga_savitzky_golay(st_parcela_int, oid):
    st_parcela_int=st_parcela_int.set_index('date')
    valores_m = range(5,80,5) # variar ventanas
    valores_d = range(2,5)
    results = pd.DataFrame(columns=['M','D','MSE'])
    best_mse = 10 # aleatorio numero inicial
    best_fit = None
    for column in st_parcela_int.columns:
        if column not in ['Manejo', 'REFSIGPAC', 'Cultivo']:
            for m in valores_m:
                for d in valores_d:
                    st_larga = savgol_filter(st_parcela_int[column], (2*m + 1), d)
                    # Calcular el error cuadrático medio (MSE)
                    mse = np.mean((st_parcela_int[column] - st_larga) ** 2)
                    if mse <= best_mse:
                        best_mse = mse
                        best_fit = st_larga
                    # Almacenar los resultados
                    row = pd.DataFrame([[m, d, mse]], columns=['M', 'D', 'MSE'])
                    results = pd.concat([results, row], axis=0, ignore_index=True)

            st_larga_best = pd.Series(best_fit, st_parcela_int.index)
            best_comb = results.loc[results['MSE'].idxmin()]

            # Imprimir los resultados
            print("Mejor combinación de m y d:")
            print(best_comb)
    
    return st_larga_best

# Dictionary to store data after long-term smoothing for conventional parcels
for parcela_id, df_parcela in sin_outliers__interpolacion_por_parcela_convencional.items():
    st_parcela_int=df_parcela.iloc[:, [i for i, col in enumerate(df_parcela.columns) if 'mean' in col or 'date' or 'Manejo' in col or 'REFSIGPAC' in col or 'Cultivo' in col]]
    st_larga_best = st_larga_savitzky_golay(st_parcela_int,parcela_id)
# Dictionary to store data after long-term smoothing for conservation parcels
for parcela_id, df_parcela in sin_outliers__interpolacion_por_parcela_conservacion.items():
    st_parcela_int=df_parcela.iloc[:, [i for i, col in enumerate(df_parcela.columns) if 'mean' in col  or 'date' or 'Manejo' in col or 'REFSIGPAC' in col or 'Cultivo' in col]]
    st_larga_best = st_larga_savitzky_golay(st_parcela_int,parcela_id)
    
    
# Best window size 11, polynomial 4, or window size 11 and polynomial 3


############################################################################################################################################
# To apply the filter, keep only the already filtered columns but maintain the dataframe with the original and filtered data for potential representation
bandas = sorted([x for x in convencional.columns.values if 'mean' in x ])
selected_columns =['date','Manejo','REFSIGPAC','Cultivo']

# Dictionary to store cleaned data for conventional parcels with selected columns

df_limpio_convencional = {}
# Loop over conventional parcel IDs and their respective dataframes

for parcela_id, df_parcela in sin_outliers__interpolacion_por_parcela_convencional.items():
    selected_columns_bandas = selected_columns.copy()

    selected_columns = ['date', 'Manejo', 'REFSIGPAC','Cultivo']    
    for banda in bandas:
        
        selected_columns_bandas.extend([banda])
        df_seleccionados = df_parcela[selected_columns_bandas]
        df_limpio_convencional[parcela_id] = df_seleccionados

# Dictionary to store cleaned data for conservation parcels with selected columns        
      
df_limpio_conservacion = {}
# Loop over conservation parcel IDs and their respective dataframes
for parcela_id, df_parcela in sin_outliers__interpolacion_por_parcela_conservacion.items():
    selected_columns_indices = selected_columns.copy()
    # Vaciar la lista selected_columns
    selected_columns = ['date', 'Manejo', 'REFSIGPAC','Cultivo']    
    for banda in bandas:
        
        selected_columns_indices.extend([banda])
        df_seleccionados = df_parcela[selected_columns_bandas]
        df_limpio_conservacion[parcela_id] = df_seleccionados     
        
############################################################################################################################################
# Function to apply Savitzky-Golay filter to a specific column in the dataframe
def st_filtro_savgol(df,indice):
    m_ = 11
    d = 3
    m = (2*m_+1)
    df[indice]=savgol_filter(df[indice],m, d)
    return df

# Dictionary to store data filtered with Savitzky-Golay for conventional parcels
df_savgol_convencional = {}
# Dictionary to store data filtered with Savitzky-Golay for conventional parcelsdf_savgol_convencional = {}
for parcela_id, df_parcela in df_limpio_convencional.items():    
    # Loop over conventional parcel IDs and their respective dataframes
    for banda in bandas:
        df_filtrado = st_filtro_savgol(df_parcela,banda)
    df_savgol_convencional[parcela_id] = df_filtrado
    
# Dictionary to store data filtered with Savitzky-Golay for conservation parcels
df_savgol_conservacion = {}
# Loop over conservation parcel IDs and their respective dataframes
for parcela_id, df_parcela in df_limpio_conservacion.items():    
    for banda in bandas:
        df_filtrado = st_filtro_savgol(df_parcela,banda)
    df_savgol_conservacion[parcela_id] = df_filtrado
    
############################################################################################################################################
# Concatenate dataframes and save them to CSV files    
    
df_bandas_convencional = pd.concat(df_limpio_convencional.values(), ignore_index=True)
df_bandas_conservacion = pd.concat(df_limpio_conservacion.values(), ignore_index=True)
# Save to CSV files
guardado_path = "C:/Users/Asier/Desktop/Proyecto ReSAg/Archivos/Comarca_III"
os.chdir(guardado_path)
df_bandas_convencional.to_csv('convencional_S1_bandas_filtrado_III.csv', index=False)

df_bandas_conservacion.to_csv('conservacion_S1_bandas_filtrado_III.csv', index=False)
