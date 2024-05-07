# Proyecto-ReSag-TFM
Codigo del proyecto realizado para el TFM dentro del marco del proyecto "Desarrollo de nuevas metodologías de teledetección para una agricultura más sostenible (ReSAg), proyecto financiado por el Ministerio de Ciencia e Innovación a través del Plan Estatal de I+D+i (PID2019-107386RB-I00)
El título del TFM es Desarrollo de metodologías de teledetección para la identificación de prácticas agrícolas sostenibles.

El código se estructura de la siguiente forma:
1- Código de Google Earth Engine para el caclulo de las estadísticas por cada parcela para las bandas de Sentinel-2 y para los índices seleccionados con el uso del filtro de nubes basado en la banda SCL.
2- Código python para la carga de los datos y representación de las series temporales previo a la eliminación de los outliers, interpolación y filtro de suavizado.
3- Código python para la carga de datos y calculo de las estadísticas zonales para los datos de Sentinel-1. Representación de series temporales.
3- Código python filtrado de outliers, interpolación y filtro de suavizado de las series temporales.
4- Código python representación de las series temporales de Sentinel-2 de los índices y bandas tras la eliminación de los outliers, interpolación y filtro de suavizado.
5- Código python de análisis estadísticos.
6-Código python estimación de los hiperparámetros óptimos para el clasificador supervisado Random Forest
7- Código python implementaciçpn clasificador supervisado Random Forest
