# Libraries
import folium
import pandas as pd
import streamlit as st
import PIL.Image as imgpil
import plotly.express as px
import haversine
import plotly.graph_objects as go
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
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y' )
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )

    # 3. Remoção de espacos das variáveis de texto
    df1.loc[:, 'ID'] =  df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Delivery_person_ID'] =  df1.loc[:, 'Delivery_person_ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] =  df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] =  df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] =  df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'Festival'] =  df1.loc[:, 'Festival'].str.strip()
    df1.loc[:, 'City'] =  df1.loc[:, 'City'].str.strip()

    # 4. Remoção de linhas vazias
    
    # 5. Limpesa da coluna de tempo (remoção de texto extra)    
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x : x.split('(min)')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    return df1

# -----------------------------------------------------
# EXTRAÇÃO
# -----------------------------------------------------
#importa dataset
def extract_data(path = 'dataset/train.csv'):
    return pd.read_csv(path)
df1 = extract_data()

# -----------------------------------------------------
# TRANSFORMAÇÃO
st.set_page_config(page_title='Visão Entregadores', page_icon='🛵', layout='wide')
# -----------------------------------------------------
# Funções:

# Limpeza
df1 = clean_code(df1)

# 10 entregadores mais rápidos e mais lentos
def top_delivers(df1, top_asc):    
    df2 = (df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
                        .groupby(['City', 'Delivery_person_ID'])
                        .mean().round(2)
                        .sort_values(['City', 'Time_taken(min)'], ascending=top_asc).reset_index())
    df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban',:].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
    
    df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
    
    return df3


# -----------------------------------------------------
# Início da estrutura logica do código
# -----------------------------------------------------

#------------------------------------------------------
# SIDEBAR
#------------------------------------------------------

st.header('Marketplace - Visão Entregadores')

# image_path = 'resources\logo_curry_company3.png'
image = imgpil.open('logo_curry_company3.png')
st.sidebar.image(image, width=128)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fatest Delivery in Town')
st.sidebar.markdown(''' ---''')

st.sidebar.markdown('Data limite')

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value     = pd.datetime (2022, 4, 13),
    min_value = pd.datetime(2022, 2, 11),
    max_value = pd.datetime(2022, 4, 6),
    format    = 'DD-MM-YYYY')


st.sidebar.markdown(''' ---''')

traffic_options = st.sidebar.multiselect('Quais as condições de táfego?',['Low', 'Medium', 'High', 'Jam'], default='Low')
st.sidebar.markdown(''' ---''')
st.sidebar.markdown('### Powered by Júlio Reis')

# Filtro de datas
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de tráfego
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

# -----------------------------------------------------
# LAYOUT STREAMLIT
# -----------------------------------------------------
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', ' ', ' '])
with tab1:
    # Métricas Gerais
    with st.container():
        st.title('Métricas Gerais')
        col1, col2, col3, col4 = st.columns(4, gap='large')

        with col1:
            # Maior idade dos entregadores
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior idade: ', maior_idade)

        with col2:
            # Menor idade dos entregadores
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor idade: ', menor_idade)

        with col3:
            # Melhor condição de veículo
            melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor condição', melhor_condicao)

        with col4:
            # Pior condição de veículo
            pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior condição', pior_condicao)

    # Avaliações
    with st.container():
        st.markdown('''---''')
        st.title('Avaliações')
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliação média por entregador')
            avg_avaliacao = df1.groupby(['Delivery_person_ID'])['Delivery_person_Ratings'].mean().round(2).reset_index()
            st.dataframe(avg_avaliacao)

        with col2:
            st.markdown('##### Avaliação média por trânsito')
            avg_traffic = (df1.loc[ :, ['Delivery_person_Ratings', 'Road_traffic_density']]
                              .groupby('Road_traffic_density')
                              .agg({'Delivery_person_Ratings' : ['mean', 'std']})).round(2)
            #Alteraçaõ do nome das colunas
            avg_traffic.columns = ['means', 'std']
            #Reset do index das colunas
            avg_traffic.reset_index()
            st.dataframe(avg_traffic)

            st.markdown('##### Avaliação média por climáticas')
            # df1.loc[linhas, colunas].groupby(coluna).mean().reset.index()
            metrics_weatherconditions = (df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions' ]]
                                            .groupby('Weatherconditions')
                                            .agg({'Delivery_person_Ratings':['mean', 'std']})).round(2)
            # alteração do nome das colunas
            metrics_weatherconditions.columns = ['means', 'std']
            # reset do index
            metrics_weatherconditions.reset_index()
            st.dataframe(metrics_weatherconditions)

    # VELOCIDADE DE ENTREGA
    with st.container():
        st.markdown('''---''')
        st.title('VELOCIDADE DE ENTREGA')

        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('##### 10 entregadores mais rápidos')
            df3 = top_delivers(df1, top_asc=True)
            st.dataframe(df3)

        with col2:
            st.markdown('##### 10 entregadores mais lentos')
            df3 = top_delivers(df1, top_asc=False)
            st.dataframe(df3)

