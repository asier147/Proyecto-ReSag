# -*- coding: utf-8 -*-
"""
Created on Mon May  6 19:22:29 2024

@author: Asier

Unfiltered Charts of Indices and Bands

"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

directory_path = "C:/Users/Asier/Desktop/Proyecto ReSAg/Archivos/S2/"

# Change the current working directory
os.chdir(directory_path)

# Load individual data files
convencional_indices = pd.read_csv("Comarca_V_indices_S2_convencional.csv")
conservacion_indices = pd.read_csv("Comarca_V_indices_S2_conservacion.csv")

convencional_bandas = pd.read_csv("Comarca_V_bandas_S2_convencional.csv")
conservacion_bandas = pd.read_csv("Comarca_V_bandas_S2_conservacion.csv")

###########################################################################################################################################################################

# Extract relevant data
indices = sorted([x for x in convencional_indices.columns.values if 'mean' in x ])
bandas = sorted([x for x in convencional_bandas.columns.values if 'mean' in x ])
columnas_fijas=['date','Manejo']

convencional_indices = convencional_indices.loc[:,columnas_fijas+indices]
conservacion_indices = conservacion_indices.loc[:,columnas_fijas+indices]

convencional_bandas = convencional_bandas.loc[:,columnas_fijas+bandas]
conservacion_bandas = conservacion_bandas.loc[:,columnas_fijas+bandas]

###########################################################################################################################################################################

# Set date format
conservacion_indices['date'] = pd.to_datetime(conservacion_indices['date']).dt.date
convencional_indices['date'] = pd.to_datetime(convencional_indices['date']).dt.date

conservacion_bandas['date'] = pd.to_datetime(conservacion_bandas['date']).dt.date
convencional_bandas['date'] = pd.to_datetime(convencional_bandas['date']).dt.date

###########################################################################################################################################################################
# Concatenate dataframes
fich_trabajo_indices = pd.concat([convencional_indices, conservacion_indices], ignore_index=True)
fich_trabajo_bandas = pd.concat([convencional_bandas, conservacion_bandas], ignore_index=True)

# Extract index and band names
indices = [col.split("_")[0] for col in indices if "mean" in col] 
bandas = [col.split("_")[0] for col in bandas if "mean" in col] 

###########################################################################################################################################################################


# Function to create percentile charts for a single index
def create_percentile_chart(index, df):
    # Group data by date and management type
    grouped = df.groupby(['date', 'Manejo'])[f'{index}_mean'].agg(['median', lambda x: np.percentile(x, 25), lambda x: np.percentile(x, 75)]).reset_index()

    # Create plot
    fig, ax = plt.subplots()
    
    for manejo in grouped['Manejo'].unique():
        subset = grouped[grouped['Manejo'] == manejo]
        color = 'forestgreen' if manejo == 'Conservacion' else 'darkgoldenrod'  
        label = f'{index} - {manejo}'
        
        # Plot medians by date
        ax.plot(subset['date'], subset['median'], label=label, color=color)
        
        # Fill area between 25th and 75th percentiles for each group
        ax.fill_between(subset['date'], subset['<lambda_0>'], subset['<lambda_1>'], color=color, alpha=0.4)
    
    # Set title, labels, and date format
    ax.set_title(f'Evolution of {index} for Different Management Types')
    ax.set_xlabel('Date')
    ax.set_ylabel('Value')
    ax.xaxis.set_major_formatter(DateFormatter('%b'))
    ax.tick_params(axis='x', rotation=45)     
    ax.legend()
    plt.show()


# Create percentile charts for indices
for index in indices:
    create_percentile_chart(index, fich_trabajo_indices)

###########################################################################################################################################################################

# Function to create percentile charts for multiple indices
def create_percentile_mult_chart(indices, df):
    fig, axes = plt.subplots(3, 3, figsize=(15, 10))  
    
    # Extract the range of years from the data
    df['date'] = pd.to_datetime(df['date'])
    min_year = df['date'].dt.year.min()
    max_year = df['date'].dt.year.max()
    
    year_str = f'{min_year}-{max_year}'
    
    fig.suptitle(f'Comparison of Indices for Different Management Types - Years {year_str}', fontsize=16)

    # Dictionary to store legend artists
    legend_artists = {}
    
    for index, ax in zip(indices, axes.flatten()):
        # Group data by date and management type
        grouped = df.groupby(['date', 'Manejo'])[f'{index}_mean'].agg(['median', lambda x: np.percentile(x, 25), lambda x: np.percentile(x, 75)]).reset_index()
        
        for manejo in grouped['Manejo'].unique():
            subset = grouped[grouped['Manejo'] == manejo]
            color = 'forestgreen' if manejo == 'Conservacion' else 'darkgoldenrod'
            label = f'{index} - {manejo}'
                    
            line = ax.plot(subset['date'], subset['median'], label=label, color=color)
            ax.fill_between(subset['date'], subset['<lambda_0>'], subset['<lambda_1>'], color=color, alpha=0.4)
            
            # Store the first element of the line for the legend
            if manejo not in legend_artists:
                legend_artists[manejo] = line[0]
        
        ax.set_title(f'Evolution of {index}')
        ax.set_ylabel('Value')
        ax.xaxis.set_major_formatter(DateFormatter('%b'))
        ax.tick_params(axis='x', rotation=45)     

    # Create a common legend
    handles = [legend_artists[key] for key in legend_artists]
    labels = [key for key in legend_artists]
    fig.legend(handles, labels, loc='upper right')

    plt.tight_layout()
    plt.show()
    
# Create percentile charts for multiple indices
create_percentile_mult_chart(indices, fich_trabajo_indices)
create_percentile_mult_chart(bandas, fich_trabajo_bandas)

###########################################################################################################################################################################
