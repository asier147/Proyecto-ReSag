# -*- coding: utf-8 -*-
"""
Created on Thu May 30 18:45:57 2024

@author: Asier
"""

import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from matplotlib.dates import DateFormatter

# Define the directory path where the files are located
directory_path = "C:/Users/Asier/Desktop/Proyecto ReSAg/Archivos/Comarca_III"

# Change the current working directory to the defined directory path
os.chdir(directory_path)

# Load individual data files
convencional_bandas = pd.read_csv('convencional_S1_bandas_filtrado_III.csv')
conservacion_bandas = pd.read_csv('conservacion_S1_bandas_filtrado_III.csv')


############################################################################################################################################

# Keep only the columns of interest
bandas = sorted([x for x in convencional_bandas.columns.values if 'mean' in x])

fixed_columns = ['date','Manejo','REFSIGPAC']
convencional_bandas = convencional_bandas.loc[:, fixed_columns + bandas]
conservacion_bandas = conservacion_bandas.loc[:, fixed_columns + bandas]

# Set the date in a more convenient format
conservacion_bandas['date'] = pd.to_datetime(conservacion_bandas['date'])
convencional_bandas['date'] = pd.to_datetime(convencional_bandas['date'])


############################################################################################################################################

# Function to create percentile plot for each band
def create_percentile_plot(banda, df):
    
    # Group data by date and management type, calculate median and percentiles
    grouped = df.groupby(['date', 'Manejo'])[f'mean_{banda}'].agg(['median', lambda x: np.percentile(x, 25), lambda x: np.percentile(x, 75)]).reset_index()

    fig, ax = plt.subplots()
    
    for manejo in grouped['Manejo'].unique():
        subset = grouped[grouped['Manejo'] == manejo]
        color = 'forestgreen' if manejo == 'Conservacion' else 'darkgoldenrod'  # Assign different colors for each management type
        label = f'{banda} - {manejo}'
               
        # Plot medians over date
        ax.plot(subset['date'], subset['median'], label=label, color=color)
        
        # Fill the area between 25th and 75th percentiles for each group
        plt.fill_between(subset['date'], subset['<lambda_0>'], subset['<lambda_1>'], color=color, alpha=0.4)
    
    ax.set_title(f'Evolución de {banda} para diferentes tipos de manejo')
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Valor')
    ax.xaxis.set_major_formatter(DateFormatter('%b'))
    ax.tick_params(axis='x', rotation=45)  # Rotate x-axis labels
    ax.legend()
    plt.show()
    
############################################################################################################################################

# Concatenate dataframes for further analysis
fich_trabajo_bandas = pd.concat([convencional_bandas, conservacion_bandas], ignore_index=True)

# Extract band names
bandas = [col.split("_")[1] for col in bandas if "mean" in col] 
   
############################################################################################################################################
    
# Create percentile plots for each band
for banda in bandas:
    create_percentile_plot(banda, fich_trabajo_bandas)

############################################################################################################################################

# Function to create a multichart comparing bands for different management types
def create_percentile_mult_chart(indices, df):
    # Define band names
    band_names = {
        'B2': 'VH',
        'B3': 'VV',
        'B4': 'VH/VV'
    }
    n_indices = len(indices)
    fig = plt.figure(figsize=(10, 15))
    gs = fig.add_gridspec(3, 2)
    
    # Create axes according to the desired layout
    axes = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, :])]
    
    # Ensure we have only as many axes as indices
    axes = axes[:n_indices]
    
    # Extract the range of years from the data
    df['date'] = pd.to_datetime(df['date'])
    min_year = df['date'].dt.year.min()
    max_year = df['date'].dt.year.max()
    region='III'
    
    year_str = f'{min_year}-{max_year}'
    
    fig.suptitle(f'Comparison of Bands for Different Management Types \n Years {year_str} in Agriculture Region {region}\n', fontsize=16)

    # Dictionary to store legend artists
    legend_artists = {}
    
    for index, ax in zip(indices, axes):
        # Group data by date and management type
        grouped = df.groupby(['date', 'Manejo'])[f'mean_{index}'].agg(['median', lambda x: np.percentile(x, 25), lambda x: np.percentile(x, 75)]).reset_index()
        
        for manejo in grouped['Manejo'].unique():
            subset = grouped[grouped['Manejo'] == manejo]
            color = 'forestgreen' if manejo == 'Conservacion' else 'darkgoldenrod'
            label = f'{index} - {manejo}'
                    
            line = ax.plot(subset['date'], subset['median'], label=label, color=color)
            ax.fill_between(subset['date'], subset['<lambda_0>'], subset['<lambda_1>'], color=color, alpha=0.4)
            
            # Store the first element of the line for the legend
            if manejo not in legend_artists:
                legend_artists[manejo] = line[0]
        
        ax.set_title(f'Evolution of {band_names[index]}')
        ax.set_ylabel('Value')
        ax.xaxis.set_major_formatter(DateFormatter('%b'))
        ax.tick_params(axis='x', rotation=45)     

    # Create a common legend
    handles = [legend_artists[key] for key in legend_artists]
    # Show the legend with appropriate labels for conservation and conventional management types

    labels = ['Conservation' if key == 'Conservacion' else 'Conventional' for key in legend_artists]   
    fig.legend(handles, labels, loc='upper right')
    # Adjust layout and display the plot

    plt.tight_layout()
    plt.show()



##########################################################################################################################################################

# Specify the directory path for saving the files
guardado_path = "C:/Users/Asier/Desktop/Proyecto ReSAg/Archivos/Comarca_III"

# Change the current working directory to the specified path
os.chdir(guardado_path)

# Save the DataFrame containing filtered bands to a CSV file without including the index
fich_trabajo_bandas.to_csv('S1_bandas_filtrado_III.csv', index=False)