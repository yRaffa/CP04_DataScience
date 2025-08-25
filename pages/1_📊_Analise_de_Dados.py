import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title='Análise de Dados', page_icon='📊', layout='wide')

st.sidebar.title("Navegação")

st.title("📊 Análise de Dados")
st.markdown("Página dedicada a análises e visualizações de dados.")

# Exemplo com dataset de demonstração
df = px.data.gapminder()

country = st.selectbox("Selecione um país:", df["country"].unique())

df_country = df[df["country"] == country]

fig = px.line(df_country, x="year", y="gdpPercap", title=f"PIB per capita - {country}")
st.plotly_chart(fig, use_container_width=True)
