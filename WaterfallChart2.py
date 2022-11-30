# https://www.kaggle.com/competitions/kaggle-survey-2021
import numpy as np 
import pandas as pd
import sidetable as stb
import plotly.graph_objects as go

survey_df_2021 = pd.read_csv('kaggle_survey_2021_responses.csv',low_memory=False,encoding='ISO-8859-1')
responses_df_2021 = survey_df_2021[1:]
survey_df_2021.to_csv('2021_kaggle_ds_and_ml_survey_responses_only.csv')

#Kagglers demographics
r_dgc_2021 = responses_df_2021.loc[:,['Q1','Q2','Q3','Q4','Q5','Q6','Q20','Q21','Q22',
                                      'Q25','Time from Start to Finish (seconds)']]
r_dgc_2020 = responses_df_2020.loc[:,['Q1','Q2','Q3','Q4','Q5','Q6','Q20','Q21','Q22',
                                      'Q25','Time from Start to Finish (seconds)']]
r_dgc_2021['Finish_time'] = r_dgc_2021['Time from Start to Finish (seconds)'].astype('int')
r_dgc_2020['Finish_time'] = r_dgc_2020['Time from Start to Finish (seconds)'].astype('int')

#Idea is to groupby and count the number of occurences of the people with set of characters. This way the demographics can be rendered quantitatively
dg_c_2021 = r_dgc_2021.groupby(['Q1','Q2','Q3','Q4','Q5','Q6','Q20','Q21','Q22','Q25'])['Finish_time'].count().reset_index()
dg_c_2020 = r_dgc_2020.groupby(['Q1','Q2','Q3','Q4','Q5','Q6','Q20','Q21','Q22','Q25'])['Finish_time'].count().reset_index()
dg_c_2021['year'] = 2021
dg_c_2020['year'] = 2020

dg_c_2021.columns = ['Age','Gender','Country','Education','Employment','Experience','Industry','Total_Employee',
                     'Datascientists','salary','Numbers','Year']
dg_c_2020.columns = ['Age','Gender','Country','Education','Employment','Experience','Industry','Total_Employee',
                     'Datascientists','salary','Numbers','Year']

visual_grp_19 = dg_c_2021.groupby(['Country','Experience'])['Numbers'].sum().reset_index()
visual_grp_19.sort_values(by='Numbers',ascending=False,inplace=True)
grp_19_total = visual_grp_19.groupby(['Country', 'Experience']).agg({'Numbers': ['sum']}).stb.subtotal().stb.flatten()
grp_19_total = grp_19_total.sort_values(by='Country')

# Need to create sub_data to get the countries total.
subtotal = grp_19_total[grp_19_total.Experience.str.contains('subtotal')]
subtotal.sort_values(by='Numbers_sum',ascending=True,inplace=True)
subtotal = subtotal[-15:]
sub_data = grp_19_total[grp_19_total.Country.isin(subtotal.Country)]

#After selecting the top 15 countries, then merge them
merge_19 = pd.merge(left=subtotal,right=sub_data,left_on='Country',right_on='Country',how='left')
merge_19.loc[(~merge_19.Experience_y.str.contains('subtotal')),
              'Numbers_sum_x'] = merge_19.loc[(~merge_19.Experience_y.str.contains('subtotal')),
                                               'Numbers_sum_y']
merge_19.drop(['Numbers_sum_y','Experience_x'],axis=1,inplace=True)   

conditionlist = [(merge_19.Experience_y.str.contains('subtotal')),
                 (~merge_19.Experience_y.str.contains('subtotal'))]
choicelist   = ['total', 'relative']
merge_19['measure'] = np.select(conditionlist, choicelist)

merge_19.loc[merge_19.Country.str.contains('Kingdom'),'Country']='UK'
merge_19.loc[merge_19.Country.str.contains('Kingdom'),'Experience_y']='UK - subtotal'

visual_19  = go.Figure()
merge_19 = merge_19[merge_19.Country == 'India'].sort_values(by='Numbers_sum_x',ascending=True)
visual_19.add_trace(go.Waterfall(x = merge_19['Experience_y'], y = merge_19['Numbers_sum_x'],
                                 measure = merge_19['measure'],
                                 text = merge_19['Numbers_sum_x'],textposition = 'outside',
                                 decreasing = {"marker":{"color":"crimson","line":{"color":"lightsalmon","width":2}}},
                                 increasing = {"marker":{"color":"forestgreen","line":{"color":"lightgreen", "width":2}}},
                                 totals     = {"marker":{"color":"mediumblue"}}
               ))
visual_19.update_layout(title_text = "Waterfall of the Experience in major countries",
                        title_font = dict(size=25,family='Verdana',
                                          color='darkred'),height =1000,width = 1000)
visual_19.update_xaxes(title = 'Experience Numbers')
visual_19.update_yaxes(title = 'Countries')
visual_19.show()