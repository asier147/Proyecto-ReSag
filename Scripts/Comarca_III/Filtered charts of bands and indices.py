
# -*- coding: utf-8 -*-
"""
Created on Mon May  6 19:22:29 2024

@author: Asier

Graficos indices y bandas filtrados

"""

import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from matplotlib.dates import DateFormatter


directory_path = "C:/Users/Asier/Desktop/Proyecto ReSAg/Archivos/Comarca_III"

# Change the current working directory
os.chdir(directory_path)

# Cargamos datos de forma individual primero
convencional_indices = pd.read_csv("convencional_III_indices_filtrado.csv")
conservacion_indices = pd.read_csv("conservacion_III_indices_filtrado.csv")
del conservacion_indices['SINDRI_median']
del convencional_indices['SINDRI_median']
convencional_bandas = pd.read_csv("convencional_III_bandas_filtrado.csv")
conservacion_bandas = pd.read_csv("conservacion_III_bandas_filtrado.csv")

###########################################################################################################################################################################

# Nos quedamos con los datos que nos interesan
indices = sorted([x for x in convencional_indices.columns.values if 'median' in x ])
bandas= sorted([x for x in convencional_bandas.columns.values if 'median' in x ])

band_order = {'B11_median': 8, 'B12_median': 9, 'B2_median': 0, 'B3_median': 1, 'B4_median': 2, 'B5_median': 3, 'B6_median': 4, 'B7_median': 5, 'B8A_median': 6, 'B8_median': 7}
bandas = sorted([x for x in convencional_bandas.columns.values if 'median' in x], key=lambda x: band_order.get(x, 10))

###########################################################################################################################################################################

columnas_fijas=['date','Manejo','Cultivo','REFSIGPAC']

convencional_indices = convencional_indices.loc[:,columnas_fijas+indices]
conservacion_indices = conservacion_indices.loc[:,columnas_fijas+indices]

convencional_bandas=convencional_bandas.loc[:,columnas_fijas+bandas]
conservacion_bandas = conservacion_bandas.loc[:,columnas_fijas+bandas]

###########################################################################################################################################################################

# Ponemos la fecha en un formato más fácil
conservacion_indices['date'] = pd.to_datetime(conservacion_indices['date'])
convencional_indices['date'] = pd.to_datetime(convencional_indices['date'])

conservacion_bandas['date'] = pd.to_datetime(conservacion_bandas['date'])
convencional_bandas['date'] = pd.to_datetime(convencional_bandas['date'])

###########################################################################################################################################################################

fich_trabajo_indices = pd.concat([convencional_indices, conservacion_indices], ignore_index=True)
fich_trabajo_bandas = pd.concat([convencional_bandas, conservacion_bandas], ignore_index=True)

indices = [col.split("_")[0] for col in indices if "median" in col] 
bandas = [col.split("_")[0] for col in bandas if "median" in col] 
   
###########################################################################################################################################################################

def crear_grafico_percentil(indice, df):
    
    grouped = df.groupby(['date', 'Manejo'])[f'{indice}_median'].agg(['median', lambda x: np.percentile(x, 25), lambda x: np.percentile(x, 75)]).reset_index()

    fig, ax = plt.subplots()
    
    for manejo in grouped['Manejo'].unique():
        subset = grouped[grouped['Manejo'] == manejo]
        color = 'forestgreen' if manejo == 'Conservacion' else 'darkgoldenrod'  # Asigna colores diferentes para cada tipo de manejo
        label = f'{indice} - {manejo}'
               
        # Traza las medianas por fecha
        ax.plot(subset['date'], subset['median'], label=label, color=color)
        
        # Rellena el área entre los percentiles 25 y 75 para cada grupo
        
        
        plt.fill_between(subset['date'], subset['<lambda_0>'], subset['<lambda_1>'], color=color,alpha=0.4)
    
    ax.set_title(f'Evolución de {indice} para diferentes tipos de manejo')
    
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Valor')
    ax.xaxis.set_major_formatter(DateFormatter('%b'))
    ax.tick_params(axis='x', rotation=45)  # Rotar las etiquetas del eje x
    ax.legend()
    plt.show()
    

for indice in indices:
    crear_grafico_percentil(indice,fich_trabajo_indices)
    
for banda in bandas:
    crear_grafico_percentil(banda,fich_trabajo_bandas)

###########################################################################################################################################################################


def crear_grafico_percentil_mult_index(indices, df):
    n_indices = len(indices)
    fig, axes = plt.subplots(5, 2, figsize=(10, 15))  
    axes = axes.flatten()
    for ax in axes[n_indices:]:
       fig.delaxes(ax)
    # Extraer el rango de años de los datos
    df['date'] = pd.to_datetime(df['date'])

    region='III'
    
    
    fig.suptitle(f'Sentinel-2 Indices  in Agriculture Region {region}\n', fontsize=16)

    
    # Diccionario para almacenar los artistas de leyenda
    legend_artists = {}
    
    for indice, ax in zip(indices, axes.flatten()):
        grouped = df.groupby(['date', 'Manejo'])[f'{indice}_median'].agg(['median', lambda x: np.percentile(x, 25), lambda x: np.percentile(x, 75)]).reset_index()
        
        for manejo in grouped['Manejo'].unique():
            subset = grouped[grouped['Manejo'] == manejo]
            color = 'forestgreen' if manejo == 'Conservacion' else 'darkgoldenrod'
            label = f'{indice} - {manejo}'
                    
            line = ax.plot(subset['date'], subset['median'], label=label, color=color)
            ax.fill_between(subset['date'], subset['<lambda_0>'], subset['<lambda_1>'], color=color, alpha=0.4)
            
            # Almacenar el primer elemento de la línea para la leyenda
            if manejo not in legend_artists:
                legend_artists[manejo] = line[0]
        
        ax.set_title(f'{indice}')
        ax.set_ylabel('Value')
        
        # Formato de fecha para mostrar solo el mes en letras
        ax.xaxis.set_major_formatter(DateFormatter('%b'))
        ax.tick_params(axis='x', rotation=45)  # Rotar las etiquetas del eje x

    # Crear una leyenda común fuera del bucle
    handles = [legend_artists[key] for key in legend_artists]
    labels = ['Conservation' if key == 'Conservacion' else 'Conventional' for key in legend_artists]   
    fig.legend(handles, labels, loc='upper right')

    # Ajustar diseño y mostrar
    plt.tight_layout()
    plt.show()


def crear_grafico_percentil_mult_bands(indices, df):
    n_indices = len(indices)
    fig, axes = plt.subplots(5, 2, figsize=(10, 15))  
    axes = axes.flatten()
    for ax in axes[n_indices:]:
       fig.delaxes(ax)
    # Extraer el rango de años de los datos
    df['date'] = pd.to_datetime(df['date'])

    region='III'
    

    
    fig.suptitle(f'Sentinel-2 Bands in Agriculture Region {region}\n', fontsize=16)

    
    
    # Diccionario para almacenar los artistas de leyenda
    legend_artists = {}
    
    for indice, ax in zip(indices, axes.flatten()):
        grouped = df.groupby(['date', 'Manejo'])[f'{indice}_median'].agg(['median', lambda x: np.percentile(x, 25), lambda x: np.percentile(x, 75)]).reset_index()
        
        for manejo in grouped['Manejo'].unique():
            subset = grouped[grouped['Manejo'] == manejo]
            color = 'forestgreen' if manejo == 'Conservacion' else 'darkgoldenrod'
            label = f'{indice} - {manejo}'
                    
            line = ax.plot(subset['date'], subset['median'], label=label, color=color)
            ax.fill_between(subset['date'], subset['<lambda_0>'], subset['<lambda_1>'], color=color, alpha=0.4)
            
            # Almacenar el primer elemento de la línea para la leyenda
            if manejo not in legend_artists:
                legend_artists[manejo] = line[0]
        
        ax.set_title(f' {indice}')
        ax.set_ylabel('Reflectance')
        
        # Formato de fecha para mostrar solo el mes en letras
        ax.xaxis.set_major_formatter(DateFormatter('%b'))
        ax.tick_params(axis='x', rotation=45)  # Rotar las etiquetas del eje x

    # Crear una leyenda común fuera del bucle
    handles = [legend_artists[key] for key in legend_artists]
    labels = ['Conservation' if key == 'Conservacion' else 'Conventional' for key in legend_artists]   
    fig.legend(handles, labels, loc='upper right')

    # Ajustar diseño y mostrar
    plt.tight_layout()
    plt.show()


crear_grafico_percentil_mult_index(indices, fich_trabajo_indices)

crear_grafico_percentil_mult_bands(bandas, fich_trabajo_bandas)

###########################################################################################################################################################################

guardado_path = "C:/Users/Asier/Desktop/Proyecto ReSAg/Archivos/Comarca_III"
os.chdir(guardado_path)
fich_trabajo_indices.to_csv('S2_indices_filtrado_III.csv', index=False)
fich_trabajo_bandas.to_csv('S2_bandas_filtrado_III.csv', index=False)
###########################################################################################################################################################################
