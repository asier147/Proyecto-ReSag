# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 15:24:15 2024

@author: Asier
"""

import os
import pandas as pd
from scipy.stats import shapiro, kruskal, mannwhitneyu


directory_path = "C:/Users/Asier/Desktop/Proyecto ReSAg/Archivos/Comarca_III"
os.chdir(directory_path)

fich_trabajo_indices= pd.read_csv("S2_indices_filtrado_III.csv")
fich_trabajo_bandas = pd.read_csv("S2_bandas_filtrado_III.csv")
fich_trabajo_radar=pd.read_csv("S1_bandas_filtrado_III.csv")

fich_trabajo_indices['date'] = pd.to_datetime(fich_trabajo_indices['date'])
fich_trabajo_bandas['date'] = pd.to_datetime(fich_trabajo_bandas['date'])
fich_trabajo_radar['date'] = pd.to_datetime(fich_trabajo_radar['date'])

indices = sorted([x for x in fich_trabajo_indices.columns.values if 'median' in x])
bandas = sorted([x for x in fich_trabajo_bandas.columns.values if 'median' in x])
bandas_radar=sorted([x for x in fich_trabajo_radar.columns.values if 'median' in x])

periodos = {
    "Prev. harvest - sowing": ('2022-07-01', '2022-09-30'),
    "Sowing- emergence": ('2022-10-01', '2022-12-31'),
    "Vegetative growth": ('2023-01-01', '2023-03-31'),
    "Reproductive phase": ('2023-04-01', '2023-05-31'),
    "Senescence": ('2023-06-01', '2023-06-30')
}

######################################################################################################################################

def create_period_dataframes(df, periodos):
    period_dataframes = []
    for periodo, (inicio, fin) in periodos.items():
        df_periodo = df[(df['date'] >= inicio) & (df['date'] <= fin)]
        period_dataframes.append((periodo, df_periodo))
    return period_dataframes
period_indices_dataframes = create_period_dataframes(fich_trabajo_indices, periodos)

for periodo, df_periodo in period_indices_dataframes:
    print(f"DataFrame para el periodo {periodo}:")
    print(df_periodo.head())
    
######################################################################################################################################
period_bandas_dataframes = create_period_dataframes(fich_trabajo_bandas, periodos)

period_radar_dataframes = create_period_dataframes(fich_trabajo_radar, periodos)

######################################################################################################################################

normalidad_indices_manejo = []
results_indices_manejo = []

# Iterar sobre cada periodo de índices
for periodo, df_periodo in period_indices_dataframes:
    for indice in indices:
        # Filtrar datos por tipo de manejo
        df_cons = df_periodo[df_periodo['Manejo'] == 'Conservacion']
        grouped_cons = df_cons.groupby(['date'])[indice].median().reset_index()
        
        df_conv = df_periodo[df_periodo['Manejo'] == 'Convencional']
        grouped_conv = df_conv.groupby(['date'])[indice].median().reset_index()
        
        # Prueba de normalidad para el grupo Convencional
        stat_conv, p_value_conv = shapiro(grouped_conv[indice])
        
        # Prueba de normalidad para el grupo Conservacion
        stat_cons, p_value_cons = shapiro(grouped_cons[indice])
        
        # Almacenar los resultados de la normalidad
        normalidad_indices_manejo.append({
            'Periodo': periodo,
            'Indice': indice,
            'Diferencia_significativa_conv': p_value_conv < 0.05,
            'Diferencia_significativa_cons': p_value_cons < 0.05,
            'Valor_p_conv': p_value_conv,
            'Valor_p_cons': p_value_cons
        })
        
        # Aplicar la prueba de Mann-Whitney U para comparar los grupos Convencional y Conservacion
        statistic, p_value = mannwhitneyu(grouped_conv[indice], grouped_cons[indice])
        
        # Almacenar los resultados de la prueba de Mann-Whitney U
        results_indices_manejo.append({
            'Periodo': periodo,
            'Indice': indice,
            'Diferencia_significativa': p_value < 0.05,
            'Valor_p': p_value
        })

# Crear DataFrames a partir de los resultados
normalidad_indices_manejo_df = pd.DataFrame(normalidad_indices_manejo)
results_indices_manejo_df = pd.DataFrame(results_indices_manejo)

# Filtrar los resultados para las pruebas de normalidad con diferencias significativas
normalidad_indices_manejo_df = normalidad_indices_manejo_df[
    (normalidad_indices_manejo_df['Diferencia_significativa_conv'] == True) | 
    (normalidad_indices_manejo_df['Diferencia_significativa_cons'] == True)
]

# Filtrar los resultados para las pruebas de Mann-Whitney U con diferencias significativas
indices_con_diferencia_manejo = results_indices_manejo_df[
    results_indices_manejo_df['Diferencia_significativa'] == True
]

# Mostrar los resultados
print(normalidad_indices_manejo_df)
print(indices_con_diferencia_manejo)
######################################################################################################################################
normalidad_bandas_manejo = []
results_bandas_manejo = []

# Iterar sobre cada periodo de índices
for periodo, df_periodo in period_bandas_dataframes:
    for banda in bandas:
        # Filtrar datos por tipo de manejo
        df_cons = df_periodo[df_periodo['Manejo'] == 'Conservacion']
        grouped_cons = df_cons.groupby(['date'])[banda].median().reset_index()
        
        df_conv = df_periodo[df_periodo['Manejo'] == 'Convencional']
        grouped_conv = df_conv.groupby(['date'])[banda].median().reset_index()
        
        # Prueba de normalidad para el grupo Convencional
        stat_conv, p_value_conv = shapiro(grouped_conv[banda])
        
        # Prueba de normalidad para el grupo Conservacion
        stat_cons, p_value_cons = shapiro(grouped_cons[banda])
        
        # Almacenar los resultados de la normalidad
        normalidad_bandas_manejo.append({
            'Periodo': periodo,
            'Banda': banda,
            'Diferencia_significativa_conv': p_value_conv < 0.05,
            'Diferencia_significativa_cons': p_value_cons < 0.05,
            'Valor_p_conv': p_value_conv,
            'Valor_p_cons': p_value_cons
        })
        
        # Aplicar la prueba de Mann-Whitney U para comparar los grupos Convencional y Conservacion
        statistic, p_value = mannwhitneyu(grouped_conv[banda], grouped_cons[banda])
        
        # Almacenar los resultados de la prueba de Mann-Whitney U
        results_bandas_manejo.append({
            'Periodo': periodo,
            'Banda': banda,
            'Diferencia_significativa': p_value < 0.05,
            'Valor_p': p_value
        })

# Crear DataFrames a partir de los resultados
normalidad_bandas_manejo_df = pd.DataFrame(normalidad_bandas_manejo)
results_bandas_manejo_df = pd.DataFrame(results_bandas_manejo)

# Filtrar los resultados para las pruebas de normalidad con diferencias significativas
normalidad_bandas_manejo_df = normalidad_bandas_manejo_df[
    (normalidad_bandas_manejo_df['Diferencia_significativa_conv'] == True) | 
    (normalidad_bandas_manejo_df['Diferencia_significativa_cons'] == True)
]

# Filtrar los resultados para las pruebas de Mann-Whitney U con diferencias significativas
bandas_con_diferencia_manejo = results_bandas_manejo_df[
    results_bandas_manejo_df['Diferencia_significativa'] == True
]

# Mostrar los resultados
print(normalidad_bandas_manejo_df)
print(bandas_con_diferencia_manejo)

######################################################################################################################################
normalidad_radar_manejo = []
results_radar_manejo = []

# Iterar sobre cada periodo de índices
for periodo, df_periodo in period_radar_dataframes:
    for band in bandas_radar:
        # Filtrar datos por tipo de manejo
        df_cons = df_periodo[df_periodo['Manejo'] == 'Conservacion']
        grouped_cons = df_cons.groupby(['date'])[band].median().reset_index()
        
        df_conv = df_periodo[df_periodo['Manejo'] == 'Convencional']
        grouped_conv = df_conv.groupby(['date'])[band].median().reset_index()
        
        # Prueba de normalidad para el grupo Convencional
        stat_conv, p_value_conv = shapiro(grouped_conv[band])
        
        # Prueba de normalidad para el grupo Conservacion
        stat_cons, p_value_cons = shapiro(grouped_cons[band])
        
        # Almacenar los resultados de la normalidad
        normalidad_radar_manejo.append({
            'Periodo': periodo,
            'Banda': band,
            'Diferencia_significativa_conv': p_value_conv < 0.05,
            'Diferencia_significativa_cons': p_value_cons < 0.05,
            'Valor_p_conv': p_value_conv,
            'Valor_p_cons': p_value_cons
        })
        
        # Aplicar la prueba de Mann-Whitney U para comparar los grupos Convencional y Conservacion
        statistic, p_value = mannwhitneyu(grouped_conv[band], grouped_cons[band])
        
        # Almacenar los resultados de la prueba de Mann-Whitney U
        results_radar_manejo.append({
            'Periodo': periodo,
            'Banda': band,
            'Diferencia_significativa': p_value < 0.05,
            'Valor_p': p_value
        })

# Crear DataFrames a partir de los resultados
normalidad_radar_manejo_df = pd.DataFrame(normalidad_radar_manejo)
results_radar_manejo_df = pd.DataFrame(results_radar_manejo)

# Filtrar los resultados para las pruebas de normalidad con diferencias significativas
normalidad_radar_manejo_df = normalidad_radar_manejo_df[
    (normalidad_radar_manejo_df['Diferencia_significativa_conv'] == True) | 
    (normalidad_radar_manejo_df['Diferencia_significativa_cons'] == True)
]

# Filtrar los resultados para las pruebas de Mann-Whitney U con diferencias significativas
radar_con_diferencia_manejo = results_radar_manejo_df[
    results_radar_manejo_df['Diferencia_significativa'] == True
]

# Mostrar los resultados
print(normalidad_radar_manejo_df)
print(radar_con_diferencia_manejo)

######################################################################################################################################
  

import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.colors as mcolors

# Define una función para formatear el valor p
def format_p_value(val):
    if val < 0.01:
        return f'{val:.3e}**'
    elif val < 0.05:
        return f'{val:.3f}*'
    else:
        return f'{val:.3f}'

period_order = [
    "Prev. harvest - sowing",
    "Sowing- emergence",
    "Vegetative growth",
    "Reproductive phase",
    "Senescence"
]

# Define la función para trazar la matriz
def plot_matrix(data, title):
    figsize = (12, 2.5)
    plt.figure(figsize=figsize)
    
    # Aplica formato a los datos
    formatted_data = data.applymap(format_p_value)
    
    sns.heatmap(data, annot=formatted_data, fmt="", cmap=cmap, linewidths=.5, cbar=False, norm=norm, annot_kws={"size": 10})
    
    plt.title(title)

        
    plt.xlabel('')
    plt.ylabel('Period', rotation=90, labelpad=30)
    data.columns = data.columns.str.replace('median_', '').str.replace('_median', '')

    plt.xticks(rotation=40)
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.show()

# Define los colores y los límites para el mapa de colores
colors = ['gold', 'khaki', 'lightgrey']
bounds = [0, 0.01, 0.05, 1]
cmap = mcolors.ListedColormap(colors)
norm = mcolors.BoundaryNorm(bounds, cmap.N)

# Convertir el orden de los periodos a categoría con el orden deseado
results_indices_manejo_df['Periodo'] = pd.Categorical(results_indices_manejo_df['Periodo'], categories=period_order, ordered=True)
results_bandas_manejo_df['Periodo'] = pd.Categorical(results_bandas_manejo_df['Periodo'], categories=period_order, ordered=True)
results_radar_manejo_df['Periodo'] = pd.Categorical(results_radar_manejo_df['Periodo'], categories=period_order, ordered=True)

# Crea la matriz para los índices
indices_matrix = results_indices_manejo_df.pivot_table(index='Periodo', columns='Indice', values='Valor_p')  # Utiliza el valor p de la prueba de normalidad para el grupo Conservacion
plot_matrix(indices_matrix, 'S-2 indices \n')


# Plot matrix for bands
bands_matrix = results_bandas_manejo_df.pivot_table(index='Periodo', columns='Banda', values='Valor_p')
desired_band_order = ['B2_median', 'B3_median', 'B4_median', 'B5_median', 'B6_median', 'B7_median', 'B8_median', 'B8A_median', 'B11_median', 'B12_median']
bands_matrix_ordered = bands_matrix.reindex(columns=desired_band_order)
plot_matrix(bands_matrix_ordered, 'S-2 Bands \n')

# Plot matrix for radar bands
radar_matrix = results_radar_manejo_df.pivot_table(index='Periodo', columns='Banda', values='Valor_p')
new_column_names = {'median_B2': 'VH','median_B3': 'VV','median_B4': 'VH/VV'}
# Assuming your DataFrame is named 'df'
radar_matrix.rename(columns=new_column_names, inplace=True)
plot_matrix(radar_matrix, 'S-1 Channels \n')


