#Importações
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

#Criando funções e importando os dados e modelo
@st.cache_data
def carregar_dados(arquivo):
    return pd.read_parquet(arquivo)

@st.cache_resource
def carregar_modelo(arquivo):
    return load(arquivo)

#Filtro para o dataframe
def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    modify = st.checkbox("Adicionar filtros")

    if not modify:
        return df

    df = df.copy()

    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filtrar dataframe por", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]

    return df


df_consolidado = carregar_dados(DADOS_CONSOLIDADOS)
df_tratado = carregar_dados(DADOS_TRATADOS)
modelo = carregar_modelo(MODELO_FINAL)

lista_retiradas = ["classificacao_co2", "classificacao_smog", "consumo_combinado_mpg", "tamanho_motor_l", "cilindros", "consumo_cidade_l_100km", "consumo_estrada_l_100km"]

df_consolidado = df_consolidado.drop(columns=lista_retiradas)

#Mudando a ordem do df_consolidado
df_consolidado = df_consolidado[
    [
        "ano_modelo",
        "marca",
        "modelo",
        "emissoes_co2_g_km",
        "tipo_combustivel",
        "classe_veiculo",
        "consumo_combinado_l_100km",
    ]
]

#Traduzindo a cooluna de tipo de combustível e aplicando no df_consolidado
combustivel = {
    "X": "gasolina_regular",
    "Z": "premium_gasoline",
    "D": "diesel",
    "E": "etanol",
    "N": "gas_natural",
}

df_consolidado["tipo_combustivel"] = df_consolidado["tipo_combustivel"].map(combustivel)

#Criando as 2 abas para o site
aba1, aba2 = st.tabs(["Dados", "Regressão"])

#Aba 1:
with aba1:
    df_filtro = filter_dataframe(df_consolidado)
    
    #DataFrame interativo
    st.dataframe(df_filtro.style.background_gradient(subset=["emissoes_co2_g_km", "consumo_combinado_l_100km"], cmap="RdYlGn_r"))

    #Separando os valores mínimo e máximo da coluna emissoes_co2_g_km
    cmin, cmax = (df_consolidado["emissoes_co2_g_km"].min(), df_consolidado["emissoes_co2_g_km"].max())

    #Gráfico de barras interativo de emissoes_co2_g_km por marca
    fig1 = px.bar(df_consolidado[["marca", "emissoes_co2_g_km"]].groupby("marca").mean().reset_index(),
                 x="marca", y="emissoes_co2_g_km", title="Média de emissão de CO<sub>2</sub> por fabricante (g/km)",
                 color="emissoes_co2_g_km", color_continuous_scale="RdYlGn_r", hover_data={"emissoes_co2_g_km": ":.2f"})
    
    fig1.update_xaxes(categoryorder="total descending")
    fig1.data[0].update(marker_cmin=cmin, marker_cmax=cmax)
    fig1.add_hline(y=df_consolidado["emissoes_co2_g_km"].mean(), line_dash="dot", line_color="purple")
    fig1.add_annotation(xref="paper", x=0.95, y=df_consolidado["emissoes_co2_g_km"].mean(), text=f"Média: {df_consolidado['emissoes_co2_g_km'].mean():.2f} g/km",
                       showarrow=False, yshift=10)
    st.plotly_chart(fig1)


    #Gráfico de barras interativo de emissoes_co2_g_km por classe_veiculo
    fig2 = px.bar(df_consolidado[["classe_veiculo", "emissoes_co2_g_km"]].groupby("classe_veiculo").mean().reset_index(),
                 x="classe_veiculo", y="emissoes_co2_g_km", title="Média de emissão de CO<sub>2</sub> por classe de veículo (g/km)",
                 color="emissoes_co2_g_km", color_continuous_scale="RdYlGn_r", hover_data={"emissoes_co2_g_km": ":.2f"})
    
    fig2.update_xaxes(categoryorder="total descending")
    fig2.data[0].update(marker_cmin=cmin, marker_cmax=cmax)
    fig2.add_hline(y=df_consolidado["emissoes_co2_g_km"].mean(), line_dash="dot", line_color="purple")
    fig2.add_annotation(xref="paper", x=0.95, y=df_consolidado["emissoes_co2_g_km"].mean(), text=f"Média: {df_consolidado['emissoes_co2_g_km'].mean():.2f} g/km",
                       showarrow=False, yshift=10)
    st.plotly_chart(fig2)


    #Gráfico de emissoes_co2_g_km por ano_modelo
    fig3 = px.bar(df_consolidado[["ano_modelo", "emissoes_co2_g_km"]].groupby("ano_modelo").mean().reset_index(),
                x="ano_modelo", y="emissoes_co2_g_km", title="Média de emissão de CO<sub>2</sub> por ano do modelo (g/km)",
                color="emissoes_co2_g_km", color_continuous_scale="RdYlGn_r", hover_data={"emissoes_co2_g_km": ":.2f"})
    
    fig3.update_xaxes(categoryorder="total descending")
    fig3.data[0].update(marker_cmin=cmin, marker_cmax=cmax)
    fig3.add_hline(y=df_consolidado["emissoes_co2_g_km"].mean(), line_dash="dot", line_color="purple")
    fig3.add_annotation(xref="paper", x=0.95, y=df_consolidado["emissoes_co2_g_km"].mean(), text=f"Média: {df_consolidado['emissoes_co2_g_km'].mean():.2f} g/km",
                       showarrow=False, yshift=10)
    st.plotly_chart(fig3)


    #Gráfico de dispersão de emissoes_co2_g_km por consumo_combinado_l_100km
    fig4 = px.scatter(df_consolidado, x="consumo_combinado_l_100km", y="emissoes_co2_g_km", title="Média de emissão de CO<sub>2</sub> por consumo (g/km)",
                      color="tipo_combustivel", color_discrete_sequence=px.colors.qualitative.Set3, opacity=0.5,
                      labels={"consumo_combinado_l_100km":"Consumo combinado (l/100 km)", "emissoes_co2_g_km":"Emissão de CO<sub>2</sub> (g/km)"})
    
    st.plotly_chart(fig4)

    
    #Gráfico de dispersão de emissoes_co2_g_km por consumo por classe_veiculo
    fig5 = px.scatter(df_consolidado, x="consumo_combinado_l_100km", y="emissoes_co2_g_km", title="Emissão de CO<sub>2</sub> x Consumo combinado - Classe de veículo",
                      color="classe_veiculo", color_discrete_sequence=px.colors.qualitative.Light24, opacity=0.5,
                      labels={"consumo_combinado_l_100km":"Consumo combinado (l/100 km)", "emissoes_co2_g_km":"Emissão de CO<sub>2</sub> (g/km)"})
    
    st.plotly_chart(fig5)

    
    #Treemap da emissoes_co2_g_km
    fig6 = px.treemap(df_consolidado, path=[px.Constant("emissoes_co2_g_km"), "marca", "classe_veiculo", "tipo_combustivel", "ano_modelo", "modelo"],
                      color="emissoes_co2_g_km", color_continuous_scale="RdYlGn_r", range_color=[cmin, cmax], title="Treemap de emissão de CO<sub>2</sub>",
                      labels={"emissoes_co2_g_km": "Emissão de CO<sub>2</sub> (g/km)"}, hover_data={"emissoes_co2_g_km": ":.2f"})

    st.plotly_chart(fig6)


#Aba 2:
with aba2:
    #Separando e ordenando os valores únicos de algumas colunas
    ano_modelo = sorted(df_tratado["ano_modelo"].unique())
    transmissao = sorted(df_tratado["transmissao"].unique())
    tipo_combustivel = sorted(df_tratado["tipo_combustivel"].unique())
    classe_veiculo_agrupada = sorted(df_tratado["classe_veiculo_agrupada"].unique())
    tamanho_motor_l_classe = sorted(df_tratado["tamanho_motor_l_classe"].unique())
    cilindros_classe = sorted(df_tratado["cilindros_classe"].unique())
    
    #Colunas sliders
    colunas_sliders = ("consumo_cidade_l_100km", "consumo_estrada_l_100km", "consumo_combinado_l_100km")

    #Definindo os valores mínimos e máximos das colunas sliders
    colunas_slider_min_max = {
        coluna: {
            "min_value": df_tratado[coluna].min(),
            "max_value": df_tratado[coluna].max()
        }
        for coluna in colunas_sliders
    }

    #Criando um formulário
    with st.form(key="formulario"):
        #Separando 2 colunas com seus widgets
        coluna_esquerda, coluna_direita = st.columns(2)

        with coluna_esquerda:
            widget_ano_modelo = st.selectbox("Ano do modelo", ano_modelo)
            widget_transmissao = st.selectbox("Transmissão", transmissao)
            widget_tipo_combustivel = st.selectbox("Tipo de combustível", tipo_combustivel)

        with coluna_direita:
            widget_classe_veiculo_agrupada = st.selectbox("Classe do veículo", classe_veiculo_agrupada)
            widget_tamanho_motor_l_classe = st.selectbox("Tamanho do motor", tamanho_motor_l_classe)
            widget_cilindros_classe = st.selectbox("Cilindros", cilindros_classe)

        #Widgets fora das colunas
        widget_consumo_cidade_l_100km = st.slider("Consumo na cidade (l/100 km)", **colunas_slider_min_max["consumo_cidade_l_100km"])
        widget_consumo_estrada_l_100km = st.slider("Consumo na estrada (l/100 km)", **colunas_slider_min_max["consumo_estrada_l_100km"])
        widget_consumo_combinado_l_100km = st.slider("Consumo combinado (l/100 km)", **colunas_slider_min_max["consumo_combinado_l_100km"])

        #Botão para gerar a previsão
        botao = st.form_submit_button(r"Prever emissão de CO$_2$")

    #Entradas do modelo
    entrada_modelo = {
        "ano_modelo": widget_ano_modelo,
        "transmissao": widget_transmissao,
        "tipo_combustivel": widget_tipo_combustivel,
        "classe_veiculo_agrupada": widget_classe_veiculo_agrupada,
        "tamanho_motor_l_classe": widget_tamanho_motor_l_classe,
        "cilindros_classe": widget_cilindros_classe,
        "consumo_cidade_l_100km": widget_consumo_cidade_l_100km, 
        "consumo_estrada_l_100km": widget_consumo_estrada_l_100km,
        "consumo_combinado_l_100km": widget_consumo_combinado_l_100km
    }

    df_entradas = pd.DataFrame([entrada_modelo])

    if botao:
        emissao = modelo.predict(df_entradas)
        st.metric(label="Emissão prevista (g/km)", value=f"{emissao[0]:.2f}")