import streamlit as st
from PIL import Image

st.set_page_config(page_title='Home', page_icon='🏠')

# image_path = 'resources/'
image = Image.open('logo_curry_company3.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown('''---''')

st.write('# Curry Company Growth Dashboard')
st.markdown(
    """
        #### Growth Dashboard foi construído para acompanhar as vendas da Curry Company analisando as metricas de crescimento dos entregadores e restaurantes.
        ### Como utilizar esse Growth Dashboard?

        - VISÃO EMPRESA
            - Visão Gerencial: São métricas gerais de crescimento dos restaurantes e dos entregadores. 
            - Visão Tática: São indicadores semanais de crescimento.
            - Visão Geográfica: são indicadores de localização central das cidades.
        - VISÃO ENTREGADORES
            - Acomapanhamento dos indicadores semanais de crescimento.
        - VISÃO RESTAURANTES
            - Acomapanhamento dos indicadores semanais dos restaurantes.
        ---
        Dúvidas: fale comigo: https://wa.me/5561991965150

    """
)
