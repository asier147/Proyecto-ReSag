
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
convencional_bandas = pd.read_csv('convencional_S1_bandas_filtrado_III.csv')
conservacion_bandas = pd.read_csv('conservacion_S1_bandas_filtrado_III.csv')


############################################################################################################################################

# Nos quedamos con los datos que nos interesan

bandas= sorted([x for x in convencional_bandas.columns.values if 'median' in x ])


columnas_fijas=['date','Manejo','REFSIGPAC']

convencional_bandas=convencional_bandas.loc[:,columnas_fijas+bandas]
conservacion_bandas = conservacion_bandas.loc[:,columnas_fijas+bandas]

# Ponemos la fecha en un formato más fácil

conservacion_bandas['date'] = pd.to_datetime(conservacion_bandas['date'])
convencional_bandas['date'] = pd.to_datetime(convencional_bandas['date'])


############################################################################################################################################

def crear_grafico_percentil(banda, df):
    
    grouped = df.groupby(['date', 'Manejo'])[f'median_{banda}'].agg(['median', lambda x: np.percentile(x, 25), lambda x: np.percentile(x, 75)]).reset_index()

    fig, ax = plt.subplots()
    
    for manejo in grouped['Manejo'].unique():
        subset = grouped[grouped['Manejo'] == manejo]
        color = 'forestgreen' if manejo == 'Conservacion' else 'darkgoldenrod'  # Asigna colores diferentes para cada tipo de manejo
        label = f'{banda} - {manejo}'
               
        # Traza las medianas por fecha
        ax.plot(subset['date'], subset['median'], label=label, color=color)
        
        # Rellena el área entre los percentiles 25 y 75 para cada grupo
        
        
        plt.fill_between(subset['date'], subset['<lambda_0>'], subset['<lambda_1>'], color=color,alpha=0.4)
    
    ax.set_title(f'Evolución de {banda} para diferentes tipos de manejo')
    
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Valor')
    ax.xaxis.set_major_formatter(DateFormatter('%b'))
    ax.tick_params(axis='x', rotation=45)  # Rotar las etiquetas del eje x
    ax.legend()
    plt.show()
    
############################################################################################################################################

fich_trabajo_bandas = pd.concat([convencional_bandas, conservacion_bandas], ignore_index=True)


bandas = [col.split("_")[1] for col in bandas if "median" in col] 
   
############################################################################################################################################
    
for banda in bandas:
    crear_grafico_percentil(banda,fich_trabajo_bandas)

############################################################################################################################################

def create_percentile_mult_chart(indices, df):
    band_names = {
        'B2': 'VH',
        'B3': 'VV',
        'B4': 'VH/VV'
    }
    n_indices = len(indices)
    fig = plt.figure(figsize=(10, 15))
    gs = fig.add_gridspec(3, 2)
    
    # Crear ejes según el diseño deseado
    axes = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, :])]
    
    # Asegurar que solo tenemos tantos ejes como índices
    axes = axes[:n_indices]
    # Extract the range of years from the data
    df['date'] = pd.to_datetime(df['date'])

    region='III'
    

    
    fig.suptitle(f'Sentinel-1 channels in Agriculture Region {region}\n', fontsize=16)

    # Dictionary to store legend artists
    legend_artists = {}
    
    for index, ax in zip(indices, axes):
        # Group data by date and management type
        grouped = df.groupby(['date', 'Manejo'])[f'median_{index}'].agg(['median', lambda x: np.percentile(x, 25), lambda x: np.percentile(x, 75)]).reset_index()
        
        for manejo in grouped['Manejo'].unique():
            subset = grouped[grouped['Manejo'] == manejo]
            color = 'forestgreen' if manejo == 'Conservacion' else 'darkgoldenrod'
            label = f'{index} - {manejo}'
                    
            line = ax.plot(subset['date'], subset['median'], label=label, color=color)
            ax.fill_between(subset['date'], subset['<lambda_0>'], subset['<lambda_1>'], color=color, alpha=0.4)
            
            # Store the first element of the line for the legend
            if manejo not in legend_artists:
                legend_artists[manejo] = line[0]
        
        ax.set_title(f'{band_names[index]}')
        ax.set_ylabel('Backscatter (dB)')
        ax.xaxis.set_major_formatter(DateFormatter('%b'))
        ax.tick_params(axis='x', rotation=45)     

    # Create a common legend
    handles = [legend_artists[key] for key in legend_artists]
    labels = ['Conservation' if key == 'Conservacion' else 'Conventional' for key in legend_artists]   
    fig.legend(handles, labels, loc='upper right')

    plt.tight_layout()
    plt.show()




create_percentile_mult_chart(bandas, fich_trabajo_bandas)


##########################################################################################################################################################

guardado_path = "C:/Users/Asier/Desktop/Proyecto ReSAg/Archivos/Comarca_III"
os.chdir(guardado_path)
fich_trabajo_bandas.to_csv('S1_bandas_filtrado_III.csv', index=False)
