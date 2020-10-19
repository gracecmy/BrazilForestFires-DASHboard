import numpy as np
import pandas as pd 
import json
import plotly.express as px
import dash
import dash_core_components as dcc 
import dash_html_components as html 
from dash.dependencies import Input,Output

#----------------------------------------------------------------- 

#the json
geo=json.load(open("brazil-states.geojson"))

#the data
df=pd.read_csv("amazon.csv",encoding="latin1")
df.drop(["date"],axis=1,inplace=True)
df.rename(columns={"year":"Year","state":"State","month":"Month","number":"Number"},inplace=True)

month_mapper={"Janeiro":"January","Fevereiro":"February","Março":"March","Abril":"April","Maio":"May","Junho":"June","Julho":"July","Agosto":"August","Setembro":"September","Outubro":"October","Novembro":"November","Dezembro":"December"}
df["Month"]=df["Month"].map(month_mapper)

name_mapper={"Acre":"Acre","Alagoas":"Alagoas","Amazonas":"Amazonas","Amapa":"Amapá","Bahia":"Bahia","Ceara":"Ceará","Distrito Federal":"Distrito Federal","Espirito Santo":"Espírito Santo","Goias":"Goiás","Maranhao":"Maranhão","Mato Grosso":"Mato Grosso","Minas Gerais":"Minas Gerais","Pará":"Pará","Paraiba":"Paraíba","Pernambuco":"Pernambuco","Piau":"Piauí","Rio":"Rio de Janeiro","Rondonia":"Rondônia","Roraima":"Roraima","Santa Catarina":"Santa Catarina","Sao Paulo":"São Paulo","Sergipe":"Sergipe","Tocantins":"Tocantins"}
df["State"]=df["State"].map(name_mapper)

state_codes=pd.read_csv("brazil-state-codes.csv")
state_codes=state_codes[["subdivision","name"]]
df=df.merge(state_codes,how="left",left_on="State",right_on="name")
df.rename(columns={"subdivision":"State_Code"},inplace=True)
df.drop(["name"],axis=1,inplace=True)

#the map data
def map_df_generator(year):
    number_i=[]
    for j in df["State"].unique():
        number_i.append(df["Number"].loc[(df["Year"]==year)&(df["State"]==j)].sum())
    df_i=pd.DataFrame({"Year":year,"State":df["State"].unique(),"State_Code":df["State_Code"].unique(),"Number":number_i})
    return df_i

df_map=pd.concat([map_df_generator(1998),map_df_generator(1999),map_df_generator(2000),map_df_generator(2001),map_df_generator(2002),map_df_generator(2003),map_df_generator(2004),map_df_generator(2005),map_df_generator(2006),map_df_generator(2007),map_df_generator(2008),map_df_generator(2009),map_df_generator(2010),map_df_generator(2011),map_df_generator(2012),map_df_generator(2013),map_df_generator(2014),map_df_generator(2015),map_df_generator(2016),map_df_generator(2017)])
df_map.reset_index(inplace=True)
df_map.drop(["index"],axis=1,inplace=True)

#----------------------------------------------------------------- 

#the text
intro_text="Brazil is home to lush rainforests which is vital for keeping our planet healthy. Unfortunately deforestation for agriculture and logging purposes has already dwindled away 20% of the Amazon rainforest. The land is usually cleared by burning which can get out of control and develop into wildfires.",html.Br(),html.Br(),"Select a state from the dropdown menu and a year from the slider to view the data."

#the dropdown
dropdown_options=[]

state_list=df["State"].unique()

for i in state_list:
    dropdown_options.append({"label":i,"value":i})

#the slider
slider_markers={1998:{"label":"1998"},2004:{"label":"2004"},2011:{"label":"2011"},2017:{"label":"2017"}}

#----------------------------------------------------------------- 

#figure_map
figure_map=px.choropleth_mapbox(df_map,geojson=geo,featureidkey='properties.sigla',locations='State_Code',color='Number',zoom=2.5,center={'lat':-13.017113,'lon':-51.074481},mapbox_style='carto-positron',color_continuous_scale="sunset",labels={"Number":"Number of Fires"},hover_name="State",hover_data={"State_Code":False,"Year":True,"Number":True},template="plotly_white")
figure_map.update_layout(margin={"t":0,"r":0,"b":0,"l":0})
figure_map.update_layout({"plot_bgcolor":"rgba(0,0,0,0)","paper_bgcolor":"rgba(0,0,0,0)"})

#figure_year
figure_year=px.bar(df,x="Year",y="Number",color="State",labels={"Number":"Number of Fires"},hover_name="State",hover_data={"State":False,"Year":False,"Month":True,"Number":True},template="plotly_white")
figure_year.update_xaxes(tick0=1998,dtick=1)
figure_year.update_layout(margin={"t":10,"r":0,"b":0,"l":80})
figure_year.update_layout({"plot_bgcolor":"rgba(0,0,0,0)","paper_bgcolor":"rgba(0,0,0,0)"})
figure_year.update_layout(showlegend=False)

#figure_month
figure_month=px.line(df,x="Month",y="Number",color="State",labels={"Number":"Number of Fires"},hover_name="State",hover_data={"State":False,"Month":False,"Year":True,"Number":True},template="plotly_white")
figure_month.update_layout(margin={"t":10,"r":0,"b":0,"l":80})
figure_month.update_layout({"plot_bgcolor":"rgba(0,0,0,0)","paper_bgcolor":"rgba(0,0,0,0)"})
figure_month.update_layout(showlegend=False)

#----------------------------------------------------------------- 

#the layout
app=dash.Dash(__name__)

app.layout=html.Div(children=[
    html.Div(children=[
        html.H1(children="Fires in Brazil",
                style={"height":"50px"}),
        html.Div(children=intro_text,
                 style={"text-align":"justify","font-family":"Georgia","display":"block"}),
        dcc.Dropdown(id="state_dropdown",options=dropdown_options,value="All States",placeholder="Select a state",
                     style={"width":"250px","margin-left":"50px","margin-top":"10px","margin-bottom":"10px"}),    
        dcc.Slider(id="year_slider",min=1998,max=2017,step=1,value=2000,marks=slider_markers),    
    ],style={"display":"inline-block","width":"40%","margin-left":"50px","margin-top":"50px","height":"450px"}),
    
    dcc.Graph(id="map_container",figure=figure_map,
              style={"display":"inline-block","width":"50%","height":"450px","vertical-align":"top","margin-top":"50px","margin-left":"20px"}),

    dcc.Graph(id="year_container",figure=figure_year,
              style={"display":"inline-block","width":"45%","height":"400px","margin-left":"50px","margin-bottom":"50px"}),

    dcc.Graph(id="month_container",figure=figure_month,
              style={"display":"inline-block","width":"45%","height":"400px","margin-bottom":"50px"}),    

],style={"background-color":"mistyrose"})

#----------------------------------------------------------------- 

#the callback
@app.callback(
    [Output(component_id="map_container",component_property="figure"),
     Output(component_id="year_container",component_property="figure"),
     Output(component_id="month_container",component_property="figure")],
    [Input(component_id="year_slider",component_property="value"),
     Input(component_id="state_dropdown",component_property="value")]
)

def update_figures(selected_year,selected_state):
    if selected_state=="All States":
        dff=df.copy()
        dfmap=dff.copy()
        dfyear=dff.copy()
        dfmonth=dff.copy()

        figure_map=px.choropleth_mapbox(dfmap, geojson=geo,featureidkey="properties.sigla",locations="State_Code",color="Number",zoom=2.5,center={"lat":-13.017113,"lon":-51.074481},mapbox_style="carto-positron",color_continuous_scale="sunset",labels={"Number":"Number of Fires"},hover_name="State",hover_data={"State_Code":False,"Year":True,"Number":True},template="plotly_white")
        figure_map.update_layout(margin={"t":0,"r":0,"b":0,"l":0})
        figure_map.update_layout({"plot_bgcolor":"rgba(0,0,0,0)","paper_bgcolor":"rgba(0,0,0,0)"})

        figure_year=px.bar(df,x="Year",y="Number",color="State",labels={"Number":"Number of Fires"},hover_name="State",hover_data={"State":False,"Year":False,"Month":True,"Number":True},template="plotly_white")
        figure_year.update_xaxes(tick0=1998,dtick=1)
        figure_year.update_layout(margin={"t":10,"r":0,"b":0,"l":80})
        figure_year.update_layout({"plot_bgcolor":"rgba(0,0,0,0)","paper_bgcolor":"rgba(0,0,0,0)"})
        figure_year.update_layout(showlegend=False)

        figure_month=px.line(df,x="Month",y="Number",color="State",labels={"Number":"Number of Fires"},hover_name="State",hover_data={"State":False,"Month":False,"Year":True,"Number":True},template="plotly_white")
        figure_month.update_layout(margin={"t":10,"r":0,"b":0,"l":80})
        figure_month.update_layout({"plot_bgcolor":"rgba(0,0,0,0)","paper_bgcolor":"rgba(0,0,0,0)"})
        figure_month.update_layout(showlegend=False)

        return figure_map,figure_year,figure_month

    else:
        dff=df.copy()
        dfyear=dff[dff["State"]==selected_state]
        dfmonth=dff[(dff["Year"]==selected_year)&(dff["State"]==selected_state)]
        dff_map=df_map.copy()
        dfmap=dff_map[dff_map["Year"]==selected_year]

        figure_map=px.choropleth_mapbox(dfmap, geojson=geo,featureidkey="properties.sigla",locations="State_Code",color="Number",zoom=2.5,center={"lat":-13.017113,"lon":-51.074481},mapbox_style="carto-positron",color_continuous_scale="sunset",labels={"Number":"Number of Fires"},hover_name="State",hover_data={"State_Code":False,"Year":True,"Number":True},template="plotly_white")
        figure_map.update_layout(margin={"t":0,"r":0,"b":0,"l":0})
        figure_map.update_layout({"plot_bgcolor":"rgba(0,0,0,0)","paper_bgcolor":"rgba(0,0,0,0)"})

        figure_year=px.bar(dfyear,x="Year",y="Number",labels={"Number":"Number of Fires"},hover_name="State",hover_data={"State":False,"Year":False,"Month":True,"Number":True},color_discrete_sequence=["tomato"],template="plotly_white")
        figure_year.update_xaxes(tick0=1998,dtick=1)
        figure_year.update_layout(margin={"t":10,"r":0,"b":0,"l":80})
        figure_year.update_layout({"plot_bgcolor":"rgba(0,0,0,0)","paper_bgcolor":"rgba(0,0,0,0)"})
        figure_year.update_layout(showlegend=False)

        figure_month=px.line(dfmonth,x="Month",y="Number",labels={"Number":"Number of Fires"},hover_name="State",hover_data={"State":False,"Month":False,"Year":True,"Number":True},color_discrete_sequence=["tomato"],template="plotly_white")
        figure_month.update_layout(margin={"t":10,"r":0,"b":0,"l":80})
        figure_month.update_layout({"plot_bgcolor":"rgba(0,0,0,0)","paper_bgcolor":"rgba(0,0,0,0)"})
        figure_month.update_layout(showlegend=False)

        return figure_map,figure_year,figure_month

#----------------------------------------------------------------- 

#the dashboard
if __name__ == '__main__':
    app.run_server(debug=True)
