import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="📊 Análise de Dados", page_icon="📊", layout="wide")

st.title("📊 Análise de Dados")
st.markdown("Aqui você poderá visualizar gráficos e explorar datasets!")

# Exemplo de dataset (pode trocar pelo seu)
df = px.data.gapminder()

# Seletor de país
country = st.selectbox("Selecione um país:", df["country"].unique())

# Filtrar dados
df_country = df[df["country"] == country]

# Exibir gráfico
fig = px.line(df_country, x="year", y="gdpPercap", title=f"PIB per capita - {country}")
st.plotly_chart(fig, use_container_width=True)
