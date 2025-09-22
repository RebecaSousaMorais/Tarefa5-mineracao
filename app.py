import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Dashboard Spotify", page_icon="🎵", layout="wide")
st.title("🎧 Dashboard Spotify: Análise de Músicas (1921–2020)")
st.markdown("Explore tendências musicais por década, gênero e artista com base em atributos de áudio e popularidade.")

# Carregamento dos dados
@st.cache_data
def carregar_dados():
    df_tracks = pd.read_csv("dataset/data.csv")
    df_tracks["year"] = pd.to_datetime(df_tracks["release_date"], errors="coerce").dt.year
    df_tracks.dropna(subset=["name", "artists", "year", "popularity"], inplace=True)

    df_artistas = pd.read_csv("dataset/data_by_artist.csv")
    df_generos = pd.read_csv("dataset/data_by_genres.csv")
    df_completo = pd.read_csv("dataset/data_w_genres.csv")

    return df_tracks, df_artistas, df_generos, df_completo

df_tracks, df_artistas, df_generos, df_completo = carregar_dados()

# Filtros interativos
st.sidebar.header("🎚️ Filtros")
anos = st.sidebar.slider("Ano de lançamento", int(df_tracks["year"].min()), int(df_tracks["year"].max()), (2000, 2020))
genero = st.sidebar.selectbox("Gênero", options=sorted(df_completo["genres"].dropna().unique()))
artista = st.sidebar.text_input("Filtrar por artista")

# Aplicando filtros
df_filtrado = df_tracks[
    (df_tracks["year"].between(*anos)) &
    (df_tracks["artists"].str.contains(artista, case=False))
]

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("🎵 Total de músicas", len(df_filtrado))
col2.metric("👤 Artista mais frequente", df_filtrado["artists"].mode()[0] if not df_filtrado.empty else "—")
col3.metric("🔥 Média de popularidade", round(df_filtrado["popularity"].mean(), 2) if not df_filtrado.empty else "—")

# Gráfico: Top 10 artistas
top_artistas = df_filtrado["artists"].value_counts().nlargest(10)
fig_bar = px.bar(
    x=top_artistas.index,
    y=top_artistas.values,
    labels={"x": "Artista", "y": "Quantidade de músicas"},
    title="🎤 Top 10 Artistas"
)
st.plotly_chart(fig_bar, use_container_width=True)

# Gráfico: Distribuição por década
df_tracks["decade"] = (df_tracks["year"] // 10) * 10
decade_counts = df_tracks["decade"].value_counts().sort_index()
fig_pie = px.pie(
    names=decade_counts.index,
    values=decade_counts.values,
    title="📆 Distribuição de músicas por década"
)
st.plotly_chart(fig_pie, use_container_width=True)

# Gráfico: Popularidade por gênero (dados agregados)
fig_genres = px.bar(
    df_generos,
    x="genres",
    y="popularity",
    title="🎧 Popularidade média por gênero",
    labels={"genres": "Gênero", "popularity": "Popularidade"}
)
st.plotly_chart(fig_genres, use_container_width=True)

# Tabela de dados
st.subheader("📋 Tabela de músicas filtradas")
st.dataframe(df_filtrado[["name", "artists", "year", "popularity"]])