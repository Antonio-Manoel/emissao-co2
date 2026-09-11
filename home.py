import pandas as pd
import plotly.express as px
import streamlit as st

from joblib import load

from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype
)

from notebooks.Apoio.config import DADOS_CONSOLIDADOS, DADOS_TRATADOS, MODELO_FINAL

@st.cache_data
#- crie duas funções, uma para a base e outra para o modelo
#- @st.cache_data para a base e @st.cache_resource
#- estudar a função disponibilizada pelo professor, a de filtrar o dataframe
#- crie 3 variáveis que recebem as 2 funções criadas, para o df consolidado, tratado e modelo
#- crie uma lista de colunas que não serão usadas na visualização e em seguida, retire elas do df consolidado
#- altere a ordem das colunas do df para ficar mais fácil para que acessa o site
#- atribua os tipos de gasolina para as letras contidas na coluna
#- crie 2 abas para o site, uma contendo dados e visualizações e a outra com a parte de regressão
#- ABA 1:
#	- use a função de importar o df(a do professor) com o df_consolidado
#	- crie o df interativo com gradiente de cores nas colunas co2_emissions_g_km, combined_l_100_km
#	- pegeu os valores mínimo máximo da coluna co2_emissions_g_km
#	- usando o px do plotly.express crie algumas figuras:
#		- gráfico de barras de emissão média por fabricante, usando um groupby das colunas make e co2_emissions_g_km, com média e index resetado. defina x, y, título, as cores dependendo da emissão e formatação de valores em duas casas decimais ao passar por cima com mouse
#		- gráfico de barras da emissão média por classe (algo parecido com o anterior)
#		- gráfico de emissão média por ano (parecido com o 1º)
#		- gráfico de dispersão de emissão por consumo de combustível (parecido com o 1º)
#		- gráfico de dispersão de emissão por consumo por classe
#		- faça um treemap da emissão de CO2
#
#- ABA 2:
#	- organize os valores únicos das colunas model_year, transmission, fuel_type, vehicle_class_grouped, engine_size_l_class, cylinders_class
#	- defina as colunas que usarão sliders: city_l_100_km, highway_l_100_km, combined_l_100_km
#	- crie um dicionário de colunas mix_max que recebe a chave contendo outro dicionário cujas chaves devem ser os valores mínimos e máximos, isso para cada coluna dos sliers
#	- crie o formulário
#	- crie 2 colunas:
#		- esquerda:
#			- crie selectbox para as colunas de anos, transmissão e combustível
#		- direita:
#			- faça a mesma coisa para as colunas do tipo de veículo, tamanho do motor e cilindros
#		- crie sliders das colunas definidas anteriormente
#		- crie o botão de submeter o formulário e prever a emissão
#		- defina as entradas do modelo como dicionário
#		- crie um df_entrada_modelo que transforma o dicionário anterior em um dataframe
#		- crie a condição par que caso o botão de previsão seja pressionado, a emissão deve ser o predict do modelo para o df anterior e por fim, deve exibir a mensagem