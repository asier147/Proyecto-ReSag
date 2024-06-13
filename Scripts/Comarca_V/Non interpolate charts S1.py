# -*- coding: utf-8 -*-
"""
Created on Sun May 19 10:54:42 2024

@author: Asier
Charts of Sentinel-1 bands

"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

dirfin = 'C:/Users/Asier/Desktop/Proyecto ReSAg/Archivos/Comarca_V/S1_V.csv'

radar=pd.read_csv(dirfin)

################################################################################################################################################################

na_counts = radar.isna().sum()
print(na_counts)
radar.info()

radar = radar.dropna()
radar = radar[(radar != 0).all(axis=1)]

################################################################################################################################################################

def crear_grafico_percentil(indice, df):
    
    grouped = df.groupby(['date', 'Manejo'])[f'median_{indice}'].agg(['median', lambda x: np.percentile(x, 25), lambda x: np.percentile(x, 75)]).reset_index()

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
    ax.set_xlabel('Date')
    ax.set_ylabel('Value')
    ax.xaxis.set_major_formatter(DateFormatter('%b'))
    ax.tick_params(axis='x', rotation=45)  # Rotar las etiquetas del eje x
    ax.legend()
    plt.show()

################################################################################################################################################################

bandas = sorted([x for x in radar.columns.values if 'median' in x or 'std' in x or 'median' in x])
bandas = [col.split("_")[1] for col in bandas if "median" in col]    

radar['date']=radar['fecha']
radar['date'] = pd.to_datetime(radar['date'], format='%Y%m%d')
radar['IDCOMARCA']='V'

################################################################################################################################################################

for banda in bandas:
    crear_grafico_percentil(banda,radar)

################################################################################################################################################################


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
    min_year = df['date'].dt.year.min()
    max_year = df['date'].dt.year.max()
    region=df['IDCOMARCA'].unique()[0]
    
    year_str = f'{min_year}-{max_year}'
    
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
    
################################################################################################################################################################


start_date = pd.to_datetime('2022-07-01')
end_date = pd.to_datetime('2023-06-30')   # Add one year for the end date
# Filter dataframe between start and end dates

radar = radar[(radar['date'] >= start_date) & (radar['date'] <= end_date)]

################################################################################################################################################################

create_percentile_mult_chart(bandas,radar)

################################################################################################################################################################
