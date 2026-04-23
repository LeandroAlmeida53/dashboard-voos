"""
Dashboard de Análise de Voos

Dashboard interativo para análise de dados de voos domésticos nos Estados Unidos.
Desenvolvido com Streamlit e Matplotlib.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Optional

# ============================================
# CONSTANTES
# ============================================

DISTANCE_BINS = [0, 500, 1000, 2000, 3000, 4000]
DATA_FILE = "flights_data.csv"

# ============================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================

st.set_page_config(
    page_title="Dashboard de Voos",
    layout="wide",
    page_icon="✈️"
)

# ============================================
# FUNÇÕES AUXILIARES
# ============================================

def format_number(value: float) -> str:
    """
    Formata números para o padrão brasileiro (ex: 1.234.567).
    """
    if pd.isna(value):
        return "-"
    return f"{value:,.0f}".replace(",", ".")


def load_data(file_path: str) -> pd.DataFrame:
    """
    Carrega dados do arquivo CSV.
    """
    return pd.read_csv(file_path)


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepara o DataFrame adicionando colunas derivadas.
    """
    df = df.copy()
    df["Year"] = df["Fly Date"].astype(str).str[:4]
    df["Month"] = df["Fly Date"].astype(str).str[4:6]
    return df


def create_distance_bins_series(distance: pd.Series, max_distance: float) -> pd.Series:
    """
    Cria bins de distância para agrupamento.
    """
    bins = DISTANCE_BINS + [max_distance]
    return pd.cut(distance, bins=bins)


# ============================================
# CARREGAMENTO DOS DADOS
# ============================================

df = load_data(DATA_FILE)
df = prepare_data(df)

# ============================================
# FILTROS (SIDEBAR)
# ============================================

st.sidebar.header("Filtros")

anos_disponiveis = sorted(df["Year"].unique())
anos_selecionados = st.sidebar.multiselect(
    "Ano",
    options=anos_disponiveis,
    default=anos_disponiveis,
    help="Selecione um ou mais anos para filtrar os dados"
)

df_filtrado = df[df["Year"].isin(anos_selecionados)]

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
    st.stop()

# ============================================
# CABEÇALHO E KPIs
# ============================================

st.title("Dashboard de Análise de Voos")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Voos",
    format_number(df_filtrado["Flights"].sum())
)
col2.metric(
    "Total Passageiros",
    format_number(df_filtrado["Passengers"].sum()))
col3.metric(
    "Rotas Únicas",
    format_number(df_filtrado.groupby(["Origin", "Destination"]).ngroups))
col4.metric(
    "Distância Média",
    f"{df_filtrado['Distance'].mean():.0f} km"
)

st.markdown("---")

# ============================================
# ABAS DE ANÁLISE
# ============================================

(
    tab_distancia,
    tab_aeroportos,
    tab_rotas,
    tab_temporal,
    tab_distribuicao
) = st.tabs([
    "📊 Por Distância",
    "🏢 Aeroportos",
    "🛫 Rotas Populares",
    "📅 Evolução Temporal",
    "📈 Distribuições"
])

# --------------------------------------------
# TAB: POR DISTÂNCIA
# --------------------------------------------

with tab_distancia:
    st.subheader("Voos e Passageiros por Intervalo de Distância")
    
    distancia_max = df_filtrado["Distance"].max()
    bins_series = create_distance_bins_series(df_filtrado["Distance"], distancia_max)
    
    grouped = df_filtrado.groupby(bins_series).agg({
        "Flights": "sum",
        "Passengers": "sum"
    })
    grouped = grouped.sort_values("Distance", ascending=False)
    grouped.index = grouped.index.astype(str)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    grouped.plot(kind="bar", ax=ax, color=["#1f77b4", "#ff7f0e"])
    ax.set_title("Voos e Passageiros por Distância")
    ax.set_xlabel("Distância (km)")
    ax.set_ylabel("Quantidade")
    ax.legend(["Voos", "Passageiros"])
    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: format_number(int(x))))
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
    
    grouped_display = grouped.reset_index()
    grouped_display.columns = ["Distância", "Voos", "Passageiros"]
    st.dataframe(grouped_display, use_container_width=True)
    
    with st.expander("📖 Legenda"):
        st.markdown("""
        **Legenda das Abreviações:**
        - **Origin**: Código IATA do aeropuerto de origem
        - **Destination**: Código IATA do aeropuerto de destino
        - **Passengers**: Número total de passageiros
        - **Flights**: Número total de voos
        - **Distance**: Distância do voo em quilômetros
        - **Fly Date**: Data do voo (formato AAAAMM)
        - **Origin City**: Cidade de origem
        - **Destination City**: Cidade de destino
        """)

# --------------------------------------------
# TAB: AEROPORTOS
# --------------------------------------------

with tab_aeroportos:
    st.subheader("Top 10 Aeroportos de Origem Mais Movimentados")
    
    aeroportos = df_filtrado.groupby("Origin").agg({
        "Flights": "sum",
        "Passengers": "sum"
    })
    top_aeroportos = aeroportos.nlargest(10, "Flights")
    
    fig, ax = plt.subplots(figsize=(10, 5))
    top_aeroportos["Flights"].plot(kind="bar", ax=ax, color="#1f77b4")
    ax.set_title("Top 10 Aeroportos de Origem")
    ax.set_xlabel("Aeroporto")
    ax.set_ylabel("Voos")
    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: format_number(int(x))))
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
    
    aeroportos_display = top_aeroportos.reset_index()
    aeroportos_display.columns = ["Aeroporto", "Voos", "Passageiros"]
    st.dataframe(aeroportos_display, use_container_width=True)
    
    with st.expander("📖 Legenda"):
        st.markdown("""
        **Legenda das Abreviações:**
        - **Origin**: Código IATA do aeropuerto de origem
        - **Flights**: Número total de voos
        - **Passengers**: Número total de passageiros
        
        **Observação**: Código IATA é um código de 3 letras que identifica aeroportos mondialmente.
        """)

# --------------------------------------------
# TAB: ROTAS POPULARES
# --------------------------------------------

with tab_rotas:
    col_esquerda, col_direita = st.columns(2)
    
    with col_esquerda:
        st.subheader("Top 10 Rotas Mais Populares")
        
        trafego = df_filtrado.groupby(["Origin", "Destination"]).agg({
            "Passengers": "sum"
        })
        rotas_populares = trafego.nlargest(10, "Passengers")
        
        fig, ax = plt.subplots(figsize=(8, 5))
        rotas_populares.plot(kind="barh", ax=ax, color="#9467bd")
        ax.set_title("Top 10 Rotas por Passageiros")
        ax.set_xlabel("Passageiros")
        ax.xaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, _: format_number(int(x))))
        plt.tight_layout()
        st.pyplot(fig)
    
    with col_direita:
        st.subheader("Top 10 Rotas por Cidade")
        
        rotas_cidade = df_filtrado.groupby(["Origin City", "Destination City"]).agg({
            "Passengers": "sum"
        })
        rotas_cidade_top = rotas_cidade.nlargest(10, "Passengers")
        
        fig, ax = plt.subplots(figsize=(8, 5))
        rotas_cidade_top.plot(kind="pie", y="Passengers", ax=ax, legend=False, autopct="%1.1f%%")
        ax.set_title("Top 10 Rotas por Passageiros")
        ax.set_ylabel("")
        plt.tight_layout()
        st.pyplot(fig)
    
    rotas_display = rotas_populares.reset_index()
    rotas_display.columns = ["Origem", "Destino", "Passageiros"]
    st.dataframe(rotas_display, use_container_width=True)
    
    with st.expander("📖 Legenda"):
        st.markdown("""
        **Legenda das Abreviações:**
        - **Origin / Origem**: Aeropuerto de origem (código IATA)
        - **Destination / Destino**: Aeropuerto de destino (código IATA)
        - **Origin City**: Cidade de origem
        - **Destination City**: Cidade de destino
        - **Passengers**: Número total de passageiros na rota
        
        **Exemplo de Rota**: "SEA → RDM" significa Seattle (SEA) para Redmond (RDM).
        """)

# --------------------------------------------
# TAB: EVOLUÇÃO TEMPORAL
# --------------------------------------------

with tab_temporal:
    col_esquerda, col_direita = st.columns(2)
    
    with col_esquerda:
        st.subheader("Voos por Ano")
        
        voos_ano = df_filtrado.groupby("Year").agg({"Flights": "sum"})
        
        fig, ax = plt.subplots(figsize=(8, 4))
        voos_ano.plot(kind="line", ax=ax, marker="o", color="#2ca02c")
        ax.set_title("Total de Voos por Ano")
        ax.set_xlabel("Ano")
        ax.set_ylabel("Voos")
        ax.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, _: format_number(int(x))))
        plt.tight_layout()
        st.pyplot(fig)
    
    with col_direita:
        st.subheader("Passageiros por Ano")
        
        passageiros_ano = df_filtrado.groupby("Year").agg({"Passengers": "sum"})
        
        fig, ax = plt.subplots(figsize=(8, 4))
        passageiros_ano.plot(kind="line", ax=ax, marker="o", color="#ff7f0e")
        ax.set_title("Total de Passageiros por Ano")
        ax.set_xlabel("Ano")
        ax.set_ylabel("Passageiros")
        ax.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, _: format_number(int(x))))
        plt.tight_layout()
        st.pyplot(fig)
    
    temporal_display = voos_ano.join(passageiros_ano).reset_index()
    temporal_display.columns = ["Ano", "Voos", "Passageiros"]
    st.dataframe(temporal_display, use_container_width=True)
    
    with st.expander("📖 Legenda"):
        st.markdown("""
        **Legenda das Abreviações:**
        - **Year**: Ano de operação
        - **Flights**: Número total de voos no ano
        - **Passengers**: Número total de passageiros transportados
        - **Fly Date**: Data do voo (formato AAAAMM)
        """)

# --------------------------------------------
# TAB: DISTRIBUIÇÕES
# --------------------------------------------

with tab_distribuicao:
    col_esquerda, col_direita = st.columns(2)
    
    with col_esquerda:
        st.subheader("Dispersão: Distância vs Passageiros")
        
        rotas_agrupadas = df_filtrado.groupby(["Origin", "Destination"]).agg({
            "Distance": "mean",
            "Passengers": "sum"
        })
        
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.scatter(
            rotas_agrupadas["Distance"],
            rotas_agrupadas["Passengers"],
            alpha=0.3,
            s=10,
            color="#1f77b4"
        )
        ax.set_title("Passageiros por Distância")
        ax.set_xlabel("Distância (km)")
        ax.set_ylabel("Passageiros")
        ax.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, _: format_number(int(x))))
        plt.tight_layout()
        st.pyplot(fig)
    
    with col_direita:
        st.subheader("Distribuição de Distâncias")
        
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(
            df_filtrado["Distance"],
            bins=50,
            color="#d62728",
            edgecolor="black",
            alpha=0.7
        )
        ax.set_title("Distribuição de Distâncias")
        ax.set_xlabel("Distância (km)")
        ax.set_ylabel("Frequência")
        ax.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, _: format_number(int(x))))
        plt.tight_layout()
        st.pyplot(fig)
    
    with st.expander("📖 Legenda"):
        st.markdown("""
        **Legenda das Abreviações:**
        - **Distance**: Distância do voo em quilômetros
        - **Passengers**: Número total de passageiros
        - **Origin / Destination**: Aeroportos de origem e destino
        
        **Observação**: O gráfico de dispersão mostra a relação entre a distância média das rotas e o número de passageiros transportados.
        """)