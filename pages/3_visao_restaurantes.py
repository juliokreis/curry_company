# Libraries
import folium as fl
import numpy as np
import pandas as pd
import streamlit as st
import PIL.Image as imgpil
import plotly.express as px
from haversine import haversine
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
st.set_page_config(page_title='Visão Restaurantes', page_icon='🍱', layout='wide')
# -----------------------------------------------------
# Funções:

# Limpeza
df1 = clean_code(df1) #salvando em df1 o retorno da chamada da função

#1. Métricas Gerais

#1.1 Entregadores únicos

#1.2 Distância média
def distance(df1, fig):
    if fig == False:
        cols = (['Restaurant_latitude', 'Restaurant_longitude',
                'Delivery_location_latitude', 'Delivery_location_longitude'])
        df1['distance'] = (df1.loc[:, cols].apply(lambda x: haversine(
            (x['Restaurant_latitude'], x['Restaurant_longitude']), 
            (x['Delivery_location_latitude'], x['Delivery_location_longitude'])),
            axis=1))

        avg_distance = np.round(df1['distance'].mean(), 2)
        return avg_distance
    
    else:
        cols = (['Restaurant_latitude', 'Restaurant_longitude','Delivery_location_latitude', 'Delivery_location_longitude'])
        df1['distance'] = (df1.loc[:, cols].apply(lambda x: haversine(
            (x['Restaurant_latitude'], x['Restaurant_longitude']),
            (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1))
    
        avg_distance = df1.loc[:, ['City', 'distance']].groupby( 'City' ).mean().reset_index()  
        fig = go.Figure ( data=[ go.Pie( labels= avg_distance['City'], values = avg_distance['distance'], pull=[0.01, 0.01, 0.01])])
    
        return fig    


#1.3 Tempo médio com Festival
#1.4 Desvio padrão com Festival
#1.5 Tempo médio sem Festival 
#1.6 Desvio Padrão sem festival

def avg_std_time_delivery(df1, festival, op):
    '''
    Função para calcular o tempo médio e o desvio padrão do tempo de entrega.
    Input: 
        df: Dataframe com dados de calculo
        op: tipo de operação para calculo 
            'avg_time': calcula o tempo médio
            'std_time': calcula o desvio padrão
    Output: 
        df: Dataframe com as colunas 'avg_time' e 'std_time' e uma linha com os valores calculados
    '''
    df_aux = (df1.loc[:, ['Time_taken(min)', 'Festival']]
            .groupby('Festival')
            .agg({'Time_taken(min)': ['mean', 'std']}))
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival, op], 2)

    return df_aux


#2. tempo médio por cidade e tipo de entrega.(tabela)

#3. O tempo médio e o desvio padrão de entrega por cidade.(Gráfico de intervalo de barras)
def avg_std_time_graph(df1):              
    df_aux = df1.loc[:, ['City', 'Time_taken(min)']].groupby('City').agg({'Time_taken(min)': [ 'mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux.round(2).reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control',
                            x=df_aux.index,
                            y=df_aux['avg_time'],
                            error_y=dict(type='data', array=df_aux['std_time'])))

    fig.update_layout(barmode='group')

    return fig

#4. A distância média dos resturantes e dos locais de entrega de cada cidade.(gráfico pizza)

#5. O tempo médio e o desvio padrão de entrega por cidade e tipo de tráfego.(gráfico sunBurst)
def avg_std_time_on_traffic(df1):
    df_aux = (df1.loc[:, ['City', 'Road_traffic_density', 'Time_taken(min)']]
            .groupby(['City', 'Road_traffic_density'])
            .agg({'Time_taken(min)': ['mean', 'std']}))
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.round(2).reset_index()
    
    fig = (px.sunburst(df_aux, path=['City', 'Road_traffic_density'], 
        values='avg_time',
        color='std_time',
        color_continuous_scale='RdBu',
        color_continuous_midpoint=np.average(df_aux['std_time'])))
    return fig


# -----------------------------------------------------
# Início da estrutura logica do código
# -----------------------------------------------------

#------------------------------------------------------
# SIDEBAR
#------------------------------------------------------

st.header('Marketplace - Visão Restaurantes')

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

traffic_options = (st.sidebar.multiselect('Quais as condições de táfego?', 
                                          ['Low', 'Medium', 'High', 'Jam'], default='Low'))
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
        st.markdown('## Métricas Gerais')

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
# .........................................................................................................
        
        with col1:
            st.markdown('Entregadores únicos')
            delivery_nunique = df1['Delivery_person_ID'].nunique()
            col1.metric('', delivery_nunique)

# .........................................................................................................

        with col2:
            st.markdown('Distância média')
            avg_distance = distance(df1, fig = False)
            col2.metric(' ', avg_distance)

# .........................................................................................................
        with col3:
            st.markdown('Tempo médio com Festival')
            df_aux = avg_std_time_delivery(df1, 'Yes', 'avg_time')
            col3.metric(' ', df_aux)

# .........................................................................................................
        with col4:
            st.markdown('Desvio padrão com Festival')
            df_aux = avg_std_time_delivery(df1, 'Yes', 'std_time')
            col4.metric(' ', df_aux)

# .........................................................................................................

        with col5:
            st.markdown('Tempo médio sem Festival')
            df_aux = avg_std_time_delivery(df1, 'No', 'avg_time')
            col5.metric(' ', df_aux)
            
# .........................................................................................................

        with col6:
            st.markdown('Desvio Padrão sem festival')
            df_aux = avg_std_time_delivery(df1, 'No', 'std_time')
            col6.metric('', df_aux)

# .........................................................................................................
# 3. O tempo médio e o desvio padrão de entrega por cidade.(Gráfico de intervalo de barras)

        with st.container():
            st.markdown('''---''')
            st.markdown('Distribuição do Tempo')
    
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('Distribuição do tempo por cidade xx')
                fig = avg_std_time_graph(df1)
                st.plotly_chart(fig)

# .........................................................................................................
#4. tempo médio por cidade e tipo de entrega.(tabela)
        with col2:
            st.markdown('###### Tempo médio por tipo de entrega')

            df_aux = (df1.loc[:, ['City', 'Type_of_order', 'Time_taken(min)']]
                        .groupby(['City', 'Type_of_order'])
                        .agg({'Time_taken(min)': ['mean', 'std']}))
            
            df_aux.columns = ['avg_time', 'std_time']
        
            st.dataframe(df_aux)


        
# .........................................................................................................
# 2. A distância média dos resturantes e dos locais de entrega de cada cidade.(gráfico pizza)

        with st.container():
            st.markdown('''---''')
            st.markdown('## Distribuição do Tempo')
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('###### Distância média - Resturantes e locais de entrega')
                fig = distance(df1, fig=True)
                st.plotly_chart(fig)

# .........................................................................................................
# 5. O tempo médio e o desvio padrão de entrega por cidade e tipo de tráfego.(gráfico sunBurst)

            with col2:
                st.markdown('###### Tempo médio por tipo de entrega')    
                fig = avg_std_time_on_traffic(df1)
                st.plotly_chart(fig)

