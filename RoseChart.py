import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import datetime, math

def jhuurl2df(url,column_name):
    ## Function to read JHU Covid Time series

    base_df = pd.read_csv(url)

    ## Unpivot
    df = base_df.melt(id_vars=['Province/State','Country/Region', 'Lat', 'Long' ], var_name='date', value_name=column_name)

    ## Column Rename and few basic transform
    df['dt_name'] = pd.to_datetime(df.date)
    df['dt'] = df.dt_name.apply(lambda x: datetime.datetime.strftime(x,'%Y-%m-%d'))
    df['country_name'] = df['Country/Region']

    ## Group By and SUM
    df = df.groupby(['country_name','dt']).agg({column_name: 'sum'}).reset_index()

    ## Prepare log values
    try:
        df['log_'+column_name] = df[column_name].apply(lambda x: 0 if x == 0 else math.log(x))
    except Exception:
        df['log_'+column_name] = 0
    return df

confirmed_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
death_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
recovered_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'

confirmed = jhuurl2df(confirmed_url,'confirmed')
deaths = jhuurl2df(death_url,'deaths')
recovered = jhuurl2df(recovered_url,'recovered')

## Read Country Details from github
country_url = 'https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.csv'
country_all = pd.read_csv(country_url)
## Map Country names with JHU names
country_all['name'] = np.select(
    [
        country_all['name'].eq('United States of America'),
        country_all['name'].eq('Bolivia (Plurinational State of)'),
        country_all['name'].eq('Brunei Darussalam'),        
        country_all['name'].eq('Myanmar'),
        country_all['name'].eq('Congo'),
        country_all['name'].eq('Congo, Democratic Republic of the'),
        country_all['name'].eq("Côte d'Ivoire"),
        country_all['name'].eq('Iran (Islamic Republic of)'),
        country_all['name'].eq("Lao People's Democratic Republic"),
        country_all['name'].eq('Moldova, Republic of'),
        country_all['name'].eq('Russian Federation'),
        country_all['name'].eq('Syrian Arab Republic'),
        country_all['name'].eq('Taiwan, Province of China'),
        country_all['name'].eq('Tanzania, United Republic of'),
        country_all['name'].eq('United Kingdom of Great Britain and Northern Ireland'),
        country_all['name'].eq('Venezuela (Bolivarian Republic of)'),
        country_all['name'].eq('Viet Nam'),
        country_all['name'].eq('Korea, Republic of')
    ], 
    [
        'US', 'Bolivia','Brunei','Burma','Congo (Brazzaville)', 'Congo (Kinshasa)', "Cote d'Ivoire", 'Iran', 'Laos',
        'Moldova', 'Russia', 'Syria', 'Taiwan*', 'Tanzania', 'United Kingdom', 'Venezuela', 'Vietnam','Korea, South'
    ], 
    default=country_all['name']
)
## Read population data
country_pop_url = 'https://raw.githubusercontent.com/datasets/population/master/data/population.csv'
country_pop = pd.read_csv(country_pop_url)
## Filter for 2018
country_pop = country_pop[(country_pop.Year == 2018)]
## Merge Country details and Population
country = country_all.merge(country_pop, left_on = 'alpha-3', right_on = 'Country Code')
country['Population'] = country['Value']
country = country[['name', 'alpha-3', 'region', 'Population']]

gdf = confirmed.merge(deaths,how='inner', on=['country_name', 'dt']).merge(recovered,how='left', on=['country_name', 'dt'])
cdr = gdf.merge(country, how='left', left_on = 'country_name', right_on = 'name')
cdr = cdr[(cdr.country_name.notnull()) & (cdr.confirmed > 0) & (cdr.region.notnull()) & (cdr.confirmed.notnull())]
cdr['confirmed_per_capita_1k'] = 1000*(cdr['confirmed']/cdr['Population'])
cdr['death_per_confirmed_1k'] = 1000*(cdr['deaths']/cdr['confirmed'])
cdr['death_per_capita_1k'] = 1000*(cdr['deaths']/cdr['Population'])
cdr['recovered_per_confirmed_1k'] = 1000*(cdr['recovered']/cdr['confirmed'])

from itertools import product
from datetime import datetime
a = range(3,13)
b = [10,20,30]
ds = []
for p in product(a,b):
    d = datetime(2020, p[0], p[1])
    ds.append(d)
    
dss = [x.strftime('%Y-%m-%d') for x in ds]
cdrn = cdr[(cdr.dt.isin(dss))].sort_values(by=['region', 'country_name','dt'])
cdrp = cdr[(cdr.dt == '2020-12-31') &  (cdr.name.notnull()) ]

#VISUALIZATION
fig = px.bar_polar(cdrn[(cdrn.region == 'Asia')].sort_values(by=['dt']), 
                   r="confirmed", 
                   theta="country_name", 
                   animation_frame="dt",
                   animation_group="country_name",
                   color="country_name",
                  
            color_discrete_sequence= px.colors.qualitative.G10,
                   log_r = True,
                  title="Comparison of Confirmed Numbers over time")
fig.show()