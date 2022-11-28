import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker
import plotly.graph_objects as go

# https://www.kaggle.com/datasets/bappekim/air-pollution-in-seoul
df = pd.read_csv('Measurement_summary.csv')
list_scode = list(set(df['Station code'])) # Código de estación, 25 en total

# Extraer el nombre del distrito de 'Address' y reemplazarlo por los  'District'
list_add = list(df['Address'])
District = [i.split(', ')[2] for i in list_add]
df['District'] = District
list_district = list(set(District)) # Lista de distritos

# Crear un nuevo DataFrame con los datos de los distritos
list_YM = [i.split(" ")[0][:-3] for i in  list(df['Measurement date'])]
list_Year = [i.split(" ")[0][:4] for i in  list(df['Measurement date'])]
list_Month = [i.split(" ")[0][5:7] for i in  list(df['Measurement date'])]
df['YM'] = list_YM
df['Year'] = list_Year
df['Month'] = list_Month
# Crear un dataframe mensual
df_monthly = df.groupby(['Station code', 'District', 'YM', 'Year', 'Month']).mean()
df_monthly = df_monthly[['SO2', 'NO2', 'O3', 'CO', 'PM10', 'PM2.5']].reset_index()

# Extraer paleta de colores, la paleta se puede cambiar
pal = list(sns.color_palette(palette='viridis', n_colors=len(list_scode)).as_hex())

fig = go.Figure()
for d,p in zip(list_district, pal):
    fig.add_trace(go.Scatter(x = df_monthly[df_monthly['District']==d]['YM'],
                             y = df_monthly[df_monthly['District']==d]['PM2.5'],
                             name = d,
                             line_color = p, 
                             fill='tozeroy'))   #tozeroy 

fig.show()