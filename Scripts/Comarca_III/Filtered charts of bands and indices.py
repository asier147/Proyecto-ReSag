# -*- coding: utf-8 -*-
"""
Created on Thu May 30 18:41:57 2024

@author: Asier
Charts of S-2 indices and bands filtered
"""

import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from matplotlib.dates import DateFormatter


directory_path = "C:/Users/Asier/Desktop/Proyecto ReSAg/Archivos/Comarca_III"

# Change the current working directory
os.chdir(directory_path)


convencional_indices = pd.read_csv("convencional_III_indices_filtrado.csv")
conservacion_indices = pd.read_csv("conservacion_III_indices_filtrado.csv")

convencional_bandas = pd.read_csv("convencional_III_bandas_filtrado.csv")
conservacion_bandas = pd.read_csv("conservacion_III_bandas_filtrado.csv")

###########################################################################################################################################################################


# We select the data we are interested in
indices = sorted([x for x in convencional_indices.columns.values if 'mean' in x ])
bands = sorted([x for x in convencional_bandas.columns.values if 'mean' in x ])

# Define the order of bands for better visualization
band_order = {'B11_mean': 8, 'B12_mean': 9, 'B2_mean': 0, 'B3_mean': 1, 'B4_mean': 2, 'B5_mean': 3, 'B6_mean': 4, 'B7_mean': 5, 'B8A_mean': 6, 'B8_mean': 7}
bands = sorted([x for x in convencional_bandas.columns.values if 'mean' in x], key=lambda x: band_order.get(x, 10))

###########################################################################################################################################################################

# Keep only selected columns
fixed_columns = ['date','Manejo','Cultivo','REFSIGPAC']
convencional_indices = convencional_indices.loc[:, fixed_columns + indices]
conservacion_indices = conservacion_indices.loc[:, fixed_columns + indices]

convencional_bandas = convencional_bandas.loc[:, fixed_columns + bands]
conservacion_bandas = conservacion_bandas.loc[:, fixed_columns + bands]

###########################################################################################################################################################################

# Set the date in a more convenient format
conservacion_indices['date'] = pd.to_datetime(conservacion_indices['date'])
convencional_indices['date'] = pd.to_datetime(convencional_indices['date'])

conservacion_bandas['date'] = pd.to_datetime(conservacion_bandas['date'])
convencional_bandas['date'] = pd.to_datetime(convencional_bandas['date'])

###########################################################################################################################################################################

# Concatenate dataframes for further analysis
working_file_indices = pd.concat([convencional_indices, conservacion_indices], ignore_index=True)
working_file_bands = pd.concat([convencional_bandas, conservacion_bandas], ignore_index=True)

indices = [col.split("_")[0] for col in indices if "mean" in col] 
bands = [col.split("_")[0] for col in bands if "mean" in col] 

###########################################################################################################################################################################

# Function to create percentile plot for an index
def create_percentile_plot(index, df):
    
    # Group data by date and management type, calculate median and percentiles
    grouped = df.groupby(['date', 'Manejo'])[f'{index}_mean'].agg(['median', lambda x: np.percentile(x, 25), lambda x: np.percentile(x, 75)]).reset_index()

    fig, ax = plt.subplots()
    
    for management in grouped['Manejo'].unique():
        subset = grouped[grouped['Manejo'] == management]
        color = 'forestgreen' if management == 'Conservacion' else 'darkgoldenrod'  # Assign different colors for each management type
        label = f'{index} - {management}'
               
        # Plot medians over date
        ax.plot(subset['date'], subset['median'], label=label, color=color)
        
        # Fill the area between 25th and 75th percentiles for each group
        plt.fill_between(subset['date'], subset['<lambda_0>'], subset['<lambda_1>'], color=color, alpha=0.4)
    
    ax.set_title(f'Evolution of {index} for Different Management Types')
    ax.set_xlabel('Date')
    ax.set_ylabel('Value')
    ax.xaxis.set_major_formatter(DateFormatter('%b'))
    ax.tick_params(axis='x', rotation=45)  # Rotate x-axis labels
    ax.legend()
    plt.show()
    

# Create percentile plots for each index
for index in indices:
    create_percentile_plot(index, working_file_indices)
    
# Create percentile plots for each band
for band in bands:
    create_percentile_plot(band, working_file_bands)

###########################################################################################################################################################################


# Define the path for saving files
save_path = "C:/Users/Asier/Desktop/Proyecto ReSAg/Archivos/Comarca_III"
os.chdir(save_path)

# Save the processed data to CSV files
working_file_indices.to_csv('S2_indices_filtrado_III.csv', index=False)
working_file_bands.to_csv('S2_bandas_filtrado_III.csv', index=False)

###########################################################################################################################################################################
