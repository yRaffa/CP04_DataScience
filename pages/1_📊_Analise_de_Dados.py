import os
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title='Análise de Dados - Games', page_icon='📊', layout='wide')
st.sidebar.title('Navegação')

def load_data():
    df = pd.read_csv('./games_db.csv')

    # Limpeza / Conversão de tipos
    df['Year_of_Release'] = pd.to_numeric(df['Year_of_Release'], errors='coerce').astype('Int64')
    df['Critic_Score'] = pd.to_numeric(df['Critic_Score'], errors='coerce')
    df['Critic_Count'] = pd.to_numeric(df['Critic_Count'], errors='coerce')
    df['User_Score'] = pd.to_numeric(df['User_Score'], errors='coerce')
    df['User_Count'] = pd.to_numeric(df['User_Count'], errors='coerce')

    for col in ['Name','Platform','Genre','Publisher','Developer','Rating']:
        if col in df.columns:
            df[col] = df[col].astype('string')

    # Converte vendas negativas para 0
    for c in ['NA_Sales','EU_Sales','JP_Sales','Other_Sales','Global_Sales']:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce').clip(lower=0)
    return df

df = load_data()
st.title('📊 Análise de Dados de Games')
st.divider()
st.caption('Escolha a Análise na Barra Lateral.')
st.caption('Use os Filtros Abaixo')

with st.expander('⚙️ Filtros', expanded=False):
    if df['Year_of_Release'].dropna().empty:
        ano_inicial, ano_final = 1980, 2025
    else:
        ano_inicial = int(df['Year_of_Release'].dropna().min())
        ano_final = int(df['Year_of_Release'].dropna().max())
    periodo = st.slider('Ano de lançamento', ano_inicial, ano_final, (ano_inicial, ano_final))

    plataformas = sorted(df['Platform'].dropna().unique().tolist()) if 'Platform' in df.columns else []
    generos = sorted(df['Genre'].dropna().unique().tolist())    if 'Genre' in df.columns else []
    publishers = sorted(df['Publisher'].dropna().unique().tolist()) if 'Publisher' in df.columns else []

    sel_plataformas = st.multiselect('Plataformas', plataformas, default=plataformas)
    sel_generos = st.multiselect('Gêneros',    generos,    default=generos)
    sel_publishers = st.multiselect('Publishers (opcional)', publishers, default=[])

# Aplica os Filtros
mask = (
    df['Year_of_Release'].between(periodo[0], periodo[1], inclusive='both')
) & (df['Platform'].isin(sel_plataformas)) & (df['Genre'].isin(sel_generos))
if sel_publishers:
    mask &= df['Publisher'].isin(sel_publishers)

df_f = df[mask].copy()

col_k1, col_k2, col_k3, col_k4 = st.columns(4)
with col_k1:
    st.metric('🎮 Jogos', f'{len(df_f):,}'.replace(",", "."))
with col_k2:
    st.metric('🌍 Vendas Globais (mi)', f"{df_f['Global_Sales'].sum():.2f}")
with col_k3:
    st.metric('📅 Período', f'{periodo[0]}–{periodo[1]}')
with col_k4:
    st.metric('🧩 Gêneros', f"{df_f['Genre'].nunique()}")

st.divider()

# Análise: tendência de lançamentos por ano
def tendencia_lancamentos(data: pd.DataFrame):
    s = data.dropna(subset=['Year_of_Release']).groupby('Year_of_Release')['Name'].count().reset_index()
    if s.empty:
        st.info('Sem dados suficientes para esta visualização.')
        return
    fig = px.line(
        s, x='Year_of_Release', y='Name', markers=True,
        title='Tendência de Lançamentos por Ano',
        labels={'Year_of_Release': 'Ano', 'Name': 'Qtde de jogos'}
    )
    fig.update_layout(template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)

# Análise: gêneros mais populares
def generos_populares(data: pd.DataFrame):
    s = data.groupby('Genre')['Name'].count().sort_values(ascending=False).reset_index()
    if s.empty:
        st.info('Sem dados suficientes para esta visualização.')
        return
    fig = px.bar(
        s, x='Genre', y='Name', text='Name',
        title='Gêneros Mais Populares (por nº de jogos)',
        labels={'Genre': 'Gênero', 'Name':'Qtde de jogos'}
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(template='plotly_dark', xaxis_tickangle=30)
    st.plotly_chart(fig, use_container_width=True)

# Análise: plataformas com mais lançamentos
def lancamentos_plataformas(data: pd.DataFrame):
    s = data.groupby('Platform')['Name'].count().sort_values(ascending=False).reset_index()
    if s.empty:
        st.info('Sem dados suficientes para esta visualização.')
        return
    fig = px.bar(
        s, x='Platform', y='Name', text='Name',
        title='Plataformas com Mais Lançamentos',
        labels={'Platform': 'Plataforma', 'Name':'Qtde de jogos'}
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)

# Análise: top 10 jogos por vendas globais
def vendas_globais(data: pd.DataFrame):
    top = (data[['Name','Platform','Global_Sales']]
           .dropna(subset=['Global_Sales'])
           .sort_values('Global_Sales', ascending=False)
           .head(10))
    if top.empty:
        st.info('Sem dados suficientes para esta visualização.')
        return
    fig = px.bar(
        top[::-1],  # inverte para mostrar o 1º no topo
        x='Global_Sales', y='Name',
        orientation='h', text='Global_Sales',
        title='Top 10 Jogos por Vendas Globais (milhões)',
        labels={'Global_Sales':'Vendas globais (mi)', 'Name':'Jogo'}
    )
    fig.update_traces(texttemplate='%{text:.2f}')
    fig.update_layout(template='plotly_dark', yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

# Análise: vendas por região
def vendas_regiao(data: pd.DataFrame):
    sales_cols = [c for c in ['NA_Sales','EU_Sales','JP_Sales','Other_Sales'] if c in data.columns]
    if not sales_cols:
        st.info('Colunas de vendas por região não encontradas.')
        return
    s = data[sales_cols].sum().reset_index()
    s.columns = ['Região','Vendas']
    if s.empty:
        st.info('Sem dados suficientes para esta visualização.')
        return
    fig = px.bar(
        s, x='Região', y='Vendas', text='Vendas',
        title='Distribuição de Vendas por Região (milhões)',
        labels={'Vendas':'Vendas (mi)'}
    )
    fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    fig.update_layout(template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)

# Análise: correlação entre notas de críticos e usuários
def correlacao_notas(data: pd.DataFrame):
    d = data[['Critic_Score','User_Score','Name','Platform','Genre']].dropna()
    if d.empty:
        st.info('Sem dados suficientes de notas nos filtros atuais.')
        return
    d = d.assign(Critic_Score_10 = d['Critic_Score'] / 10.0)

    # tenta trendline OLS (statsmodels); se não houver, mostra sem tendência
    try:
        fig = px.scatter(
            d, x='Critic_Score_10', y='User_Score',
            hover_data=['Name','Platform','Genre'],
            trendline='ols',
            title='Correlação: Nota de Críticos (0–10) x Usuários (0–10)',
            labels={'Critic_Score_10':'Críticos (0–10)', 'User_Score':'Usuários (0–10)'}
        )
    except Exception:
        st.warning("Trendline OLS indisponível (instale 'statsmodels'). Exibindo scatter sem tendência.")
        fig = px.scatter(
            d, x='Critic_Score_10', y='User_Score',
            hover_data=['Name','Platform','Genre'],
            title='Correlação: Nota de Críticos (0–10) x Usuários (0–10)',
            labels={'Critic_Score_10':'Críticos (0–10)', 'User_Score':'Usuários (0–10)'}
        )
    fig.update_layout(template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)

# Análise: vendas por classificação etária
def vendas_classificacao_etaria(data: pd.DataFrame):
    if 'Rating' not in data.columns or data['Rating'].dropna().empty:
        st.info('Sem dados de classificação etária (Rating) para os filtros atuais.')
        return
    s = data.dropna(subset=['Rating']).groupby('Rating')['Global_Sales'].sum().reset_index()
    s = s.sort_values('Global_Sales', ascending=False)
    if s.empty:
        st.info('Sem dados suficientes para esta visualização.')
        return
    fig = px.bar(
        s, x='Rating', y='Global_Sales', text='Global_Sales',
        title='Vendas Globais por Classificação Etária (milhões)',
        labels={'Rating':'Rating', 'Global_Sales':'Vendas (mi)'}
    )
    fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    fig.update_layout(template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)

#Visao geral dos dados
def visao_geral():
    st.subheader('📌 Visão Geral dos Dados')
    with st.expander('Visualizar amostra da base', expanded=False):
        st.dataframe(df_f.head(25), use_container_width=True)

analises = st.sidebar.radio(
    'Escolha a análise',
    [
        'Visão Geral',
        'Tendência de Lançamentos por Ano',
        'Gêneros Mais Populares',
        'Plataformas com Mais Lançamentos',
        'Top 10 Jogos por Vendas Globais',
        'Vendas por Região',
        'Notas: Críticos vs Usuários',
        'Vendas por Classificação Etária (Rating)'
    ],
    index=0
)

def mostrar_dicionario_variaveis():
    data = [("Name", "Qualitativa", "Nominal", "Nome do jogo → identificação, não possui ordem."),
            ("Platform", "Qualitativa", "Nominal", "Plataforma (PS4, Xbox, etc.), categorias sem hierarquia."),
            ("Year_of_Release", "Quantitativa", "Discreta", "Anos inteiros (1980, 2005...), não fracionados."),
            ("Genre", "Qualitativa", "Nominal", "Categoria de jogo (Action, Sports, RPG...), sem hierarquia."),
            ("Publisher", "Qualitativa", "Nominal", "Nome da empresa (Nintendo, EA, etc.), apenas rótulos."),
            ("Developer", "Qualitativa", "Nominal", "Nome do estúdio desenvolvedor, apenas rótulos."),
            ("Rating", "Qualitativa", "Ordinal", "Classificação etária (E, T, M, AO...), ordem implícita."),
            ("NA_Sales", "Quantitativa", "Contínua", "Vendas em milhões (pode ser 1.52, 0.03, etc.)."),
            ("EU_Sales", "Quantitativa", "Contínua", "Vendas na Europa, fracionadas."),
            ("JP_Sales", "Quantitativa", "Contínua", "Vendas no Japão, fracionadas."),
            ("Other_Sales", "Quantitativa", "Contínua", "Vendas em outras regiões, fracionadas."),
            ("Global_Sales", "Quantitativa", "Contínua", "Soma das vendas, fracionadas."),
            ("Critic_Score", "Quantitativa", "Contínua", "Nota média (0–100), pode ter decimais."),
            ("Critic_Count", "Quantitativa", "Discreta", "Número de críticos (contagem inteira)."),
            ("User_Score", "Quantitativa", "Contínua", "Nota média (0–10), pode ter decimais."),
            ("User_Count", "Quantitativa", "Discreta", "Número de usuários (contagem inteira).")]
    df_dict = pd.DataFrame(data, columns=["Coluna", "Tipo", "Subtipo", "Justificativa"])
    st.dataframe(df_dict, use_container_width=True)

# Switch-case para exibir a análise escolhida
match analises:
    case 'Visão Geral':
        st.subheader('📌 Visão Geral dos Dados')
        st.write('Base de dados: Vendas e Análises de Jogos *(1980 - 2020)*')
        with st.expander('Visualizar amostra da base', expanded=False):
            st.dataframe(df_f.head(25), use_container_width=True)
        st.divider()
        st.subheader('📋 Descrição das Colunas')
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('''
            - **Name**: Nome do jogo
            - **Platform**: Plataforma (ex: PS4, XOne, PC)
            - **Year_of_Release**: Ano de lançamento
            - **Genre**: Gênero do jogo (ex: Action, Sports)
            - **Publisher**: Empresa publicadora
            - **Developer**: Empresa desenvolvedora
            - **Other_Sales**: Vendas em outras regiões (milhões)
            - **Global_Sales**: Vendas globais (milhões)
            ''')
        with col2:
            st.markdown('''
            - **NA_Sales**: Vendas na América do Norte (milhões)
            - **EU_Sales**: Vendas na Europa (milhões)
            - **JP_Sales**: Vendas no Japão (milhões)
            - **Critic_Score**: Nota média dos críticos (0-100)
            - **Critic_Count**: Número de críticas recebidas
            - **User_Score**: Nota média dos usuários (0-10)
            - **User_Count**: Número de avaliações dos usuários
            - **Rating**: Classificação etária (ESRB) (ex: E, T, M)
            ''')
        st.divider()
        st.subheader('📈 Identificação do tipo das variáveis')
        mostrar_dicionario_variaveis()
        st.divider()
        st.subheader('❔ Principais Perguntas da Análise de Dados')
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('''
            >**1. Tendência de Lançamentos por Ano**
            - Quais anos tiveram picos ou quedas significativas?
            - Existe uma tendência de crescimento ou declínio no número de lançamentos?
            \n
            >**2. Gêneros Mais Populares**
            - Quais são os gêneros mais populares em termos de lançamentos?
            - Quais gêneros geram mais vendas globais?
            \n
            >**3. Plataformas com Mais Lançamentos**
            - Quais plataformas têm o maior número de lançamentos?
            - Existe uma correlação entre o número de lançamentos e as vendas globais por plataforma?
            \n
            >**4. Vendas por Região**
            - Quais regiões apresentam as maiores vendas de jogos?
            - Existem diferenças significativas nas preferências de jogos entre regiões?
            ''')
        with col2:
            st.markdown('''
            >**5. Notas: Críticos vs Usuários**
            - Quais jogos apresentam maior discrepância entre as avaliações de críticos e usuários?
            - As notas influenciam as vendas globais dos jogos?
            \n
            >**6. Vendas por Classificação Etária**
            - Quais classificações etárias (ESRB) geram mais vendas?
            - Como a distribuição de vendas por classificação etária mudou ao longo do tempo?
            \n
            >**7. Publicadoras e Desenvolvedoras**
            - Quais publicadoras e desenvolvedoras lançaram mais jogos?
            - Quais publicadoras têm os jogos mais bem avaliados?
            \n
            >**8. Jogos de Maior Sucesso**
            - Quais jogos tiveram as maiores vendas globais?
            - Quais são os jogos mais populares por gênero?
            ''')

    case 'Tendência de Lançamentos por Ano':
        st.subheader('📈 Tendência de Lançamentos por Ano')
        tendencia_lancamentos(df_f)

    case 'Gêneros Mais Populares':
        st.subheader('🎭 Gêneros Mais Populares')
        generos_populares(df_f)

    case 'Plataformas com Mais Lançamentos':
        st.subheader('💻 Plataformas com Mais Lançamentos')
        lancamentos_plataformas(df_f)

    case 'Top 10 Jogos por Vendas Globais':
        st.subheader('🏆 Top 10 Jogos por Vendas Globais')
        vendas_globais(df_f)

    case 'Vendas por Região':
        st.subheader('🌍 Vendas por Região')
        vendas_regiao(df_f)

    case 'Notas: Críticos vs Usuários':
        st.subheader('⭐ Correlação de Notas: Críticos vs Usuários')
        correlacao_notas(df_f)

    case 'Vendas por Classificação Etária (Rating)':
        st.subheader('🔞 Vendas por Classificação Etária')
        vendas_classificacao_etaria(df_f)

    case _:
        st.warning("Selecione uma análise válida na barra lateral.")
