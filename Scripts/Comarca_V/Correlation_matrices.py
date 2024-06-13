# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 17:19:35 2024

@author: Asier

Correlación índices
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


directory_path = "C:/Users/Asier/Desktop/Proyecto ReSAg/Archivos/Comarca_V/"
os.chdir(directory_path)

convencional_indices = pd.read_csv("convencional_V_indices_filtrado.csv")
conservacion_indices = pd.read_csv("conservacion_V_indices_filtrado.csv")

del convencional_indices['SINDRI_median']
del conservacion_indices['SINDRI_median']
convencional_bandas = pd.read_csv("convencional_V_bandas_filtrado.csv")
desired_order = [col for col in convencional_bandas.columns if col not in ['B8A_median','B11_median', 'B12_median']] + ['B8A_median','B11_median', 'B12_median']
convencional_bandas=convencional_bandas[desired_order]


conservacion_bandas = pd.read_csv("conservacion_V_bandas_filtrado.csv")
desired_order = [col for col in conservacion_bandas.columns if col not in ['B8A_median','B11_median', 'B12_median']] + ['B8A_median','B11_median', 'B12_median']
conservacion_bandas=conservacion_bandas[desired_order]


fich_trabajo_radar=pd.read_csv("S1_bandas_filtrado_V.csv")
radar_convencional=fich_trabajo_radar[fich_trabajo_radar['Manejo']=='Convencional']
radar_conservacion=fich_trabajo_radar[fich_trabajo_radar['Manejo']=='Conservacion']
##########################################################################################################

columnas=['date','Manejo','REFSIGPAC','Cultivo']
indices = sorted([x for x in convencional_indices.columns.values if 'median' in x])
convencional_indices=convencional_indices[columnas+indices]
conservacion_indices=conservacion_indices[columnas+indices]

##########################################################################################################
fich_trabajo_convencional = pd.merge(convencional_indices, convencional_bandas,on=['date','Manejo','REFSIGPAC','Cultivo'], how='outer')
fich_trabajo_convencional = pd.merge(fich_trabajo_convencional, radar_convencional,on=['date','Manejo','REFSIGPAC'], how='outer')

fich_trabajo_convencional = fich_trabajo_convencional[(fich_trabajo_convencional['date'] >= '2022-07-01') & (fich_trabajo_convencional['date'] <= '2023-08-31')]

fich_trabajo_conservacion = pd.merge(conservacion_indices, conservacion_bandas,on=['date','Manejo','REFSIGPAC','Cultivo'], how='outer')
fich_trabajo_conservacion = fich_trabajo_conservacion[(fich_trabajo_conservacion['date'] >= '2022-11-01') & (fich_trabajo_conservacion['date'] <= '2023-08-31')]
fich_trabajo_conservacion = pd.merge(fich_trabajo_conservacion, radar_conservacion,on=['date','Manejo','REFSIGPAC'], how='outer')

indices = [col.split("_")[0] for col in indices if "median" in col]

##########################################################################################################
# Calculate correlation matrices for both datasets
columnas_convencional = ['date'] + [col for col in fich_trabajo_convencional.columns if 'median' in col]
df_convencional = fich_trabajo_convencional[columnas_convencional].set_index('date')
correlation_matrix_convencional = df_convencional.corr().values

columnas_conservacion = ['date'] + [col for col in fich_trabajo_conservacion.columns if 'median' in col]
df_conservacion = fich_trabajo_conservacion[columnas_conservacion].set_index('date')
correlation_matrix_conservacion = df_conservacion.corr().values

# Ensure both matrices are of the same size and have the same labels
assert correlation_matrix_convencional.shape == correlation_matrix_conservacion.shape
index_names = df_convencional.columns.tolist()

# Create combined correlation matrix
combined_matrix = np.zeros_like(correlation_matrix_convencional)
# Fill upper triangle with conservacion correlations
upper_triangle_indices = np.triu_indices_from(combined_matrix, k=0)
combined_matrix[upper_triangle_indices] = correlation_matrix_conservacion[upper_triangle_indices]
# Fill lower triangle with convencional correlations
lower_triangle_indices = np.tril_indices_from(combined_matrix, k=-1)
combined_matrix[lower_triangle_indices] = correlation_matrix_convencional[lower_triangle_indices]

# Define the mapping
specific_mapping = {

    "median_B2": "VH",
    "median_B3": "VV",
    "median_B4": "VH/VV"
}

def process_name(name):
    if '_median' in name:
        return name.split('_median')[0]
    return specific_mapping.get(name, name)

modified_index_names = [process_name(name) for name in index_names]
# Plotting the combined correlation matrix
plt.figure(figsize=(10, 8))
plt.imshow(combined_matrix, cmap='coolwarm', interpolation='nearest')

# Configure axis labels
plt.xticks(range(len(modified_index_names)), modified_index_names, rotation=45, ha='right')
plt.yticks(range(len(modified_index_names)), modified_index_names)
# Add correlation values to each cell
for i in range(len(index_names)):
    for j in range(len(index_names)):
        if (i, j) in zip(*upper_triangle_indices) or (i, j) in zip(*lower_triangle_indices):
            plt.text(j, i, f'{combined_matrix[i, j]:.2f}', ha='center', va='center', color='white')

# Add colorbar and title
plt.colorbar(label='Correlation')
plt.title('Combined Correlation Matrix\nUpper: Conservation, Lower: Conventional')
plt.tight_layout()
plt.show()
##########################################################################################################
