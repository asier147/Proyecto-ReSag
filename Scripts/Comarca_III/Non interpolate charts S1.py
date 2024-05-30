# -*- coding: utf-8 -*-
"""
Created on Thu May 30 18:04:30 2024

@author: Asier
Non interpolate Charts of Sentinel-1 bands
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

# Load radar data from CSV file
dirfin = 'C:/Users/Asier/Desktop/Proyecto ReSAg/Archivos/Comarca_III/S1_ASC_103_III.csv'
radar = pd.read_csv(dirfin)

# Display NA counts and data info
na_counts = radar.isna().sum()
print(na_counts)
radar.info()

# Drop rows with NA values and zero values
radar = radar.dropna()
radar = radar[(radar != 0).all(axis=1)]

# Function to create percentile charts for a single index
def crear_grafico_percentil(indice, df):
    # Group data by date and management type, calculate median and percentiles
    grouped = df.groupby(['date', 'Manejo'])[f'mean_{indice}'].agg(['median', lambda x: np.percentile(x, 25), lambda x: np.percentile(x, 75)]).reset_index()
    
    # Create plot
    fig, ax = plt.subplots()
    for manejo in grouped['Manejo'].unique():
        subset = grouped[grouped['Manejo'] == manejo]
        color = 'forestgreen' if manejo == 'Conservacion' else 'darkgoldenrod'  # Assign colors based on management type
        label = f'{indice} - {manejo}'
        
        # Plot medians by date
        ax.plot(subset['date'], subset['median'], label=label, color=color)
        
        # Fill area between 25th and 75th percentiles
        plt.fill_between(subset['date'], subset['<lambda_0>'], subset['<lambda_1>'], color=color, alpha=0.4)
    
    # Set title, labels, and date format
    ax.set_title(f'Evolución de {indice} para diferentes tipos de manejo')
    ax.set_xlabel('Date')
    ax.set_ylabel('Value')
    ax.xaxis.set_major_formatter(DateFormatter('%b'))
    ax.tick_params(axis='x', rotation=45)  # Rotate x-axis labels
    ax.legend()
    plt.show()

# Extract band names from columns
bandas = sorted([x for x in radar.columns.values if 'mean' in x])
bandas = [col.split("_")[1] for col in bandas if "mean" in col]    

# Add and format date column
radar['date'] = radar['fecha']
radar['date'] = pd.to_datetime(radar['date'], format='%Y%m%d')
radar['IDCOMARCA'] = 'III'

# Create percentile charts for each band
for banda in bandas:
    crear_grafico_percentil(banda, radar)

# Function to create percentile charts for multiple indices
def create_percentile_mult_chart(indices, df):
    band_names = {'B2': 'VH', 'B3': 'VV', 'B4': 'VH/VV'}
    n_indices = len(indices)
    fig = plt.figure(figsize=(10, 15))
    gs = fig.add_gridspec(3, 2)
    
    # Create axes according to desired layout
    axes = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, :])]
    
    # Ensure only as many axes as indices
    axes = axes[:n_indices]
    # Extract the range of years from the data
    df['date'] = pd.to_datetime(df['date'])
    min_year = df['date'].dt.year.min()
    max_year = df['date'].dt.year.max()
    region = df['IDCOMARCA'].unique()[0]
    
    year_str = f'{min_year}-{max_year}'
    fig.suptitle(f'Comparison of Bands for Different Management Types \n Years {year_str} in Agriculture Region {region}\n', fontsize=16)

    # Dictionary to store legend artists
    legend_artists = {}
    
    for index, ax in zip(indices, axes):
        # Group data by date and management type, calculate median and percentiles
        grouped = df.groupby(['date', 'Manejo'])[f'mean_{index}'].agg(['median', lambda x: np.percentile(x, 25), lambda x: np.percentile(x, 75)]).reset_index()
        
        for manejo in grouped['Manejo'].unique():
            subset = grouped[grouped['Manejo'] == manejo]
            color = 'forestgreen' if manejo == 'Conservacion' else 'darkgoldenrod'
            label = f'{index} - {manejo}'
            
            # Plot medians and fill area between 25th and 75th percentiles
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
    labels = ['Conservation' if key == 'Conservacion' else 'Conventional' for key in legend_artists]
    fig.legend(handles, labels, loc='upper right')

    plt.tight_layout()
    plt.show()

# Filter dataframe between start and end dates
start_date = pd.to_datetime('2022-07-01')
end_date = pd.to_datetime('2023-06-30')
radar = radar[(radar['date'] >= start_date) & (radar['date'] <= end_date)]

# Create percentile charts for multiple indices
create_percentile_mult_chart(bandas, radar)
