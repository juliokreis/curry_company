# Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go


import folium
import pandas as pd
import PIL.Image as imgpil
import streamlit as st

from streamlit_folium import folium_static

# -----------------------------------------------------
# LIMPEZA
# -----------------------------------------------------


def clean_code(df1):
    '''
    Esta função tem a responsabilidade de limpar o dataframe

    Tipos de limpeza:
    1. Remoção dos dados NaN
    2. Mudança do tipo da coluna de dados
    3. Remoção de espacos das variáveis de texto
    4. Remoção de linhas vazias
    5. Limpesa da coluna de tempo (remoção de texto extra)

    Input: Dataframe
    Output: Dataframe
    '''
    # 1. Remoção dos dados NaN
    linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    linhas_selecionadas = (df1['Festival'] != 'NaN')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    linhas_selecionadas = (df1['City'] != 'NaN')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    linhas_selecionadas = (df1['Weatherconditions'] != 'NaN')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    # 2. Mudança do tipo da coluna de dados
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(
        float)
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    # 3. Remoção de espacos das variáveis de texto
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Delivery_person_ID'] = df1.loc[:,
                                               'Delivery_person_ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:,
                                                 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()

    # 4. Remoção de linhas vazias

    # 5. Limpesa da coluna de tempo (remoção de texto extra)
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(
        lambda x: x.split('(min)')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    return df1

# -----------------------------------------------------
# EXTRAÇÃO
# -----------------------------------------------------
# importa dataset


def extract_data(path='dataset/train.csv'):
    return pd.read_csv(path)


df1 = extract_data()

# -----------------------------------------------------
# TRANSFORMAÇÃO
st.set_page_config(page_title='Visão Empresa', page_icon='🏭', layout='wide')
# -----------------------------------------------------
# Funções:

# Limpeza
df1 = clean_code(df1)

# 6. Localização central de cada cidade


def country_maps(df1):
    df_aux = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude',
                         'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()

    map = folium.Map()

    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
                   location_info['Delivery_location_longitude']],
                  popup=location_info[['City', 'Road_traffic_density']]).add_to(map)
    folium_static(map, width=1024, height=600)

# 5. Quantidade de pedidos entregues por entregador e por semana


def order_share_by_week(df1):
    # Quantidade de pedidos por entregador e por semana
    df_aux01 = df1.loc[:, ['ID', 'week_of_year']].groupby(
        ['week_of_year']).count().reset_index()
    df_aux02 = (df1.loc[:, ['Delivery_person_ID', 'week_of_year']]
                   .groupby(['week_of_year'])
                   .nunique()
                   .reset_index())

    df_aux = pd.merge(df_aux01, df_aux02, how='inner', on='week_of_year')
    df_aux['order_by_delivery'] = (
        df_aux['ID'] / df_aux['Delivery_person_ID']).round(2)

    # Visualização do gráfico
    fig = px.line(df_aux, x='week_of_year', y='order_by_delivery')
    return fig

# 4. Quantidade de pedidos entregues por semana


def order_by_week(df1):
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby(
        'week_of_year').count().reset_index()
    fig = px.line(df_aux, x='week_of_year', y='ID')

    return fig

# 3. Comparação de pedidos por cidade e tráfego


def traffic_order_city(df1):
    # Comparação da quantidade de entregas pelo tipo de tráfego
    df_aux = (df1.loc[:, ['ID', 'City', 'Road_traffic_density']]
              .groupby(['City', 'Road_traffic_density'])
              .count()
              .reset_index())
    # visualização do gráfico de bolhas
    # fig = px.bar(df_aux, x='City', y='ID', color='Road_traffic_density', barmode='group')
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density',
                     size='ID', color='City')
    return fig

# 2. Pedidos por tipo de tráfego


def traffic_order_share(df1):
    # quantidade de pedidos por tipo de tráfego
    df_aux = (df1.loc[:, ['ID', 'Road_traffic_density']]
                 .groupby('Road_traffic_density')
                 .count()
                 .reset_index())
    # quantidade de pedidos por tipo de tráfego
    df_aux['percent_ID'] = 100 * (df_aux['ID'] / df_aux['ID'].sum())
    # renderização do gráfico de pizza
    fig = px.pie(df_aux, values='percent_ID', names='Road_traffic_density')

    return fig

# 1. Pedidos por dia


def order_metric(df1):
    cols = ['ID', 'Order_Date']
    df_aux = (df1.loc[:, cols].groupby(['Order_Date']).count().reset_index())

    # renderização do gráfico de linhas
    fig = px.bar(df_aux, x='Order_Date', y='ID')

    return fig


# -----------------------------------------------------
# Início da estrutura logica do código
# -----------------------------------------------------
order_metric(df1)
traffic_order_share(df1)
traffic_order_city(df1)
order_by_week(df1)
order_share_by_week(df1)

# ------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------
st.header('Marketplace - Visão Empresa')

# image_path = 'resources\logo_curry_company3.png'
image = imgpil.open('logo_curry_company3.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fatest Delivery in Town')
st.sidebar.markdown('''---''')

st.sidebar.markdown('Selecione uma data limite')

date_slider = st.sidebar.slider('Até qual valor',
                                value=pd.datetime(2022, 4, 13),
                                min_value=pd.datetime(2022, 2, 11),
                                max_value=pd.datetime(2022, 4, 6),
                                format='DD-MM-YYY')

st.sidebar.markdown(''' ---''')

traffic_options = st.sidebar.multiselect('Quais as condições de táfego?',
                                         ['Low', 'Medium', 'High', 'Jam'],
                                         default=['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown(''' ---''')
st.sidebar.markdown('''## Powered by Júlio Reis''')

# Filtro de datas
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de tráfego
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

# ----------------------------------------------------------------------------------------------
# LAYOUT STREAMLIT
# ----------------------------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(
    ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])
# Visão Gerencial
with tab1:
    with st.container():
        # 1. Order metric
        st.markdown('Order by Day')
        fig = order_metric(df1)
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            # 2. traffic_order_share
            st.markdown('Distribuição de pedidos por tráfego')
            fig = traffic_order_share(df1)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # 3. traffic_order_city
            st.markdown('Comparação de pedidos por cidade e tráfego')
            fig = traffic_order_city(df1)
            st.plotly_chart(fig, use_container_width=True)
# ---------------------------------------------------------------------------------
# Visão Tática
with tab2:
    with st.container():
        st.markdown('Quantidade de pedidos por semana')
        fig = order_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown('Quantidade de pedidos por entregador e por semana')
        fig = order_share_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)

 # ----------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------
# Visão geográfica
with tab3:
    # Métrica 4. Localização central de cidade por tráfego.
    st.markdown('localização central de cidade por tráfego')
    country_maps(df1)

# CARGA----------------------------------------------------------------------------
df1 = extract_data()
df1.to_csv('dataset/df1.csv', index=False)
