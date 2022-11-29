# https://www.kaggle.com/datasets/shivamb/netflix-shows
import pandas as pd
import numpy as np
import plotly.graph_objects as go

df = pd.read_csv('netflix_titles.csv')
# data cleaning
df = df.dropna( how='any',subset=['cast', 'director'])
df = df.dropna()

# converting into proper date time format
df["date_added"] = pd.to_datetime(df['date_added'])
df['year_added'] = df['date_added'].dt.year
df['month_added'] = df['date_added'].dt.month
# finding seasons from durations
df['season_count'] = df.apply(lambda x : x['duration'].split(" ")[0] if "Season" in x['duration'] else "", axis = 1)
df['duration'] = df.apply(lambda x : x['duration'].split(" ")[0] if "Season" not in x['duration'] else "", axis = 1)
df = df.rename(columns={"listed_in":"genre"})
df['genre'] = df['genre'].apply(lambda x: x.split(",")[0])

d2 = df[df["type"] == "Movie"]
col = "year_added"

vc2 = d2[col].value_counts().reset_index().rename(columns = {col : "count", "index" : col})
vc2['percent'] = vc2['count'].apply(lambda x : 100*x/sum(vc2['count']))
vc2 = vc2.sort_values(col)

fig2 = go.Figure(go.Waterfall(
    name = "Movie", orientation = "v", 
    x = ["2008", "2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021"],
    textposition = "auto",
    text = ["1", "2", "1", "13", "3", "6", "14", "48", "204", "743", "1121", "1366", "1228", "84"],
    y = [1, 2, -1, 13, -3, 6, 14, 48, 204, 743, 1121, 1366, -1228, -84],
    connector = {"line":{"color":"#b20710"}},
    increasing = {"marker":{"color":"#b20710"}},
    decreasing = {"marker":{"color":"orange"}},
))

fig2.update_xaxes(showgrid=False)
fig2.update_yaxes(showgrid=False, visible=False)
fig2.update_traces(hovertemplate=None)
fig2.update_layout(title='Watching Movies over the year', height=350,
                   margin=dict(t=80, b=20, l=50, r=50),
                   hovermode="x unified",
                   xaxis_title=' ', yaxis_title=" ",
                   plot_bgcolor='#333', paper_bgcolor='#333',
                   title_font=dict(size=25, color='#8a8d93', family="Lato, sans-serif"),
                   font=dict(color='#8a8d93'))
fig2.show()
