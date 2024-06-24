# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 09:46:06 2024

@author: Asier Herrera
"""

import os
import glob
import numpy as np
import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt

def _stats_(df):
    media = df.mean()
    std = df.std()
    mediana = df.median()
    q1 = df.quantile(.25)
    q3 = df.quantile(.75)
    return media, std, mediana, q1, q3

def _arrows_(ax, sup_90, sup_80, C, maxval, dist_arrow = 300):
    if maxval-5000 < 3000: maxval = maxval + 2000
    ax.axvline(x = 0.8, ymin = 0, ymax = 0.98, c = 'k')
    ax.axvline(x = 0.9, ymin = 0, ymax = 0.6, c = 'k')
    ax.axvline(x = 1, ymin = 0, ymax = 0.98, c = 'k')
    ax.annotate(text='', xy=(1,5000), xytext=(0.9,5000), arrowprops=dict(arrowstyle='<->'))
    ax.annotate(text='', xy=(1,maxval + dist_arrow), xytext=(0.8,maxval + dist_arrow), arrowprops=dict(arrowstyle='<->'))
    txt = '{}% parcels'.format(round(sup_90/len(C)*100))
    ax.annotate(text=txt, xy=(1,5100), xytext=(0.92,5100))
    txt = '{}% parcels'.format(round(sup_80/len(C)*100))
    ax.annotate(text=txt, xy=(1,maxval - dist_arrow), xytext=(0.87,maxval - dist_arrow))
    
def _max_val_(CA, CT, bins = 50):
    val1 = pd.DataFrame(np.histogram(CA[colint], bins = bins)).T
    val1 = val1.loc[val1[1]>0.8]
    val1 = val1[0].max()
    val2 = pd.DataFrame(np.histogram(CT[colint], bins = bins)).T
    val2 = val2.loc[val2[1]>0.8]
    val2 = val2[0].max()
    return max(val1, val2)
# colint = ['Conservacion', 'Convencional'] 
colint = 'Probability'
archivos = glob.glob(r"C:\Users\Asier\Desktop\Proyecto ReSAg\Archivos\RF_total\*\*Probabilidad*xlsx")
RES = []
# fig_g, axs_g = plt.subplots(7,2, figsize = (15,20), sharex = True, sharey = True)
for i,archivo in enumerate(archivos):
    print(archivo)
    config = os.path.basename(archivo).split('_')[0]
    df = pd.read_excel(archivo, index_col = 0)
    res = []
    df[colint] = df[['Convencional','Conservacion']].max(axis = 1)
    #Estadisticas generales
    media_g, std_g, mediana_g, q1_g, q3_g = _stats_(df[colint])
    
    #Estadisticas por manejo:
    CT = df.loc[df['Manejo'] == 'Convencional']
    media_ct, std_ct, mediana_ct, q1_ct, q3_ct = _stats_(CT[colint])
    CA = df.loc[df['Manejo'] == 'Conservacion']
    media_ca, std_ca, mediana_ca, q1_ca, q3_ca = _stats_(CA[colint])
    bins = 50
    max_val = _max_val_(CA, CT, bins = bins)
    #nº parcelas por encima de X%:
    # sup_90 = (df[colint] >= 0.9).sum() # del total
    # sup_80 = (df[colint] >= 0.8).sum() # del total
    
    sup_90_ct = (CT[colint] >= 0.9).sum()
    sup_90_ca = (CA[colint] >= 0.9).sum()
    sup_80_ct = (CT[colint] >= 0.8).sum()
    sup_80_ca = (CA[colint] >= 0.8).sum()
    RES.append([config,media_g, media_ca, media_ct])
    #Graficos de resultados:
    fig, axs = plt.subplots(1,2, figsize = (15,5), sharey = True)
    ax = axs[0]
    # ax = axs_g[i,0]
    #Conservacion
    sns.histplot(CA[colint], bins = bins, ax = ax)
    # if i == 0: ax.set_title('Conservation')
    ax.set_ylabel('{}\nNº parcels'.format(config))
    _arrows_(ax, sup_90_ca, sup_80_ca, CA, max_val)
    #Convencional
    ax = axs[1]
    # ax = axs_g[i,1]
    sns.histplot(CT[colint], bins = bins, ax = ax)
    if i == 0: ax.set_title('Conventional')
    _arrows_(ax, sup_90_ct, sup_80_ct, CT, max_val)
    # fig_g.tight_layout()
    fig.tight_layout()
    
    #sns.boxplot(data = df, x = 'Manejo', y = colint)
    
df_res = pd.DataFrame(RES, columns = ['Config.','General','Convservacion','Convencional'])    
df_res.to_excel(r"C:\Users\Asier\Desktop\Proyecto ReSAg\Archivos\RF_total\Resumen_probabilidades.xlsx", index = False)
