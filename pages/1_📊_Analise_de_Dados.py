import os
import streamlit as st
import pandas as pd
import plotly.express as px
from scipy.stats import ttest_ind

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

# Medidas centrais e distribuições
def medidas_centrais(data: pd.DataFrame):
    # Notas de usuários x críticos
    st.subheader("⭐ Notas: Medidas Centrais e Correlação")

    notas = data[['Critic_Score','User_Score']].dropna()
    if notas.empty:
        st.warning("Sem dados suficientes de notas para esta seção.")
    else:
        # Normaliza a nota dos críticos para a mesma escala 0–10
        notas = notas.assign(Critic_Score_10 = notas['Critic_Score'] / 10.0)

        # Medidas centrais das notas
        cs_mean = notas['Critic_Score_10'].mean()
        cs_median = notas['Critic_Score_10'].median()
        cs_std = notas['Critic_Score_10'].std()

        us_mean = notas['User_Score'].mean()
        us_median = notas['User_Score'].median()
        us_std = notas['User_Score'].std()

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Críticos — Média (0–10)", f"{cs_mean:.2f}")
            st.metric("Usuários — Média (0–10)", f"{us_mean:.2f}")
        with c2:
            st.metric("Críticos — Mediana (0–10)", f"{cs_median:.2f}")
            st.metric("Usuários — Mediana (0–10)", f"{us_median:.2f}")
        with c3:
            st.metric("Críticos — Desvio Padrão", f"{cs_std:.2f}")
            st.metric("Usuários — Desvio Padrão", f"{us_std:.2f}")

        # Correlação (Pearson)
        corr = notas[['Critic_Score_10','User_Score']].corr().iloc[0,1]
        st.info(f"Coeficiente de correlação entre notas de **Críticos (0–10)** e **Usuários (0–10)**: **{corr:.2f}**")

        # Scatter com trendline quando possível
        try:
            fig_scatter = px.scatter(
                notas, x='Critic_Score_10', y='User_Score',
                title="Correlação: Críticos (0–10) x Usuários (0–10)",
                labels={'Critic_Score_10':'Críticos (0–10)', 'User_Score':'Usuários (0–10)'},
                trendline='ols'
            )
        except Exception:
            st.warning("Trendline OLS indisponível (instale 'statsmodels'). Exibindo sem tendência.")
            fig_scatter = px.scatter(
                notas, x='Critic_Score_10', y='User_Score',
                title="Correlação: Críticos (0–10) x Usuários (0–10)",
                labels={'Critic_Score_10':'Críticos (0–10)', 'User_Score':'Usuários (0–10)'},
            )
        fig_scatter.update_layout(template='plotly_dark')
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.divider()

    # Médias de vendas por região
    st.subheader("🌍 Médias de Vendas por Região")

    sales_cols = [c for c in ['NA_Sales','EU_Sales','JP_Sales','Other_Sales'] if c in data.columns]
    if not sales_cols:
        st.warning("Colunas de vendas regionais não encontradas.")
        return

    means = data[sales_cols].mean().rename_axis("Região").reset_index(name="Média_Vendas")
    fig_reg = px.bar(
        means, x='Região', y='Média_Vendas', text='Média_Vendas',
        title="Médias de Vendas por Região (mi por jogo)",
        labels={'Média_Vendas':'Média (mi)'}
    )
    fig_reg.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig_reg.update_layout(template='plotly_dark')
    st.plotly_chart(fig_reg, use_container_width=True)

    # Insight automático sobre a ordem das regiões
    order = means.sort_values('Média_Vendas', ascending=False)['Região'].tolist()
    ordem_str = " > ".join(order)
    st.caption(f"**Ordem das médias por região (maior → menor):** {ordem_str}")
    if all(r in order for r in ['NA_Sales','EU_Sales','JP_Sales']):
        if order.index('NA_Sales') < order.index('EU_Sales') < order.index('JP_Sales'):
            st.success("Nos dados filtrados, confirma-se: **NA > EU > JP**.")
        else:
            st.info("Para os filtros atuais, a ordem **NA > EU > JP** não se mantém exatamente; veja o ranking acima.")

# Teste de hipótese: jogos de Ação vendem mais que RPG?

def teste_acao_vs_rpg(data: pd.DataFrame):
    st.write("**H₀**: A média de vendas globais de jogos de Ação = média de RPG")
    st.write("**H₁**: A média de vendas globais de jogos de Ação > média de RPG")

    acao = data.loc[data['Genre'] == 'Action', 'Global_Sales'].dropna()
    rpg = data.loc[data['Genre'] == 'Role-Playing', 'Global_Sales'].dropna()

    if acao.empty or rpg.empty:
        st.warning("Não há dados suficientes para comparar Ação vs RPG.")
        return

    # teste t
    stat, p = ttest_ind(acao, rpg, alternative='greater', equal_var=False)

    st.write(f"Estatística t: **{stat:.3f}**")
    st.write(f"P-Valor: **{p:.5f}**")
    st.write(f"Nível de Significância: **0.05 (5%)**")

    if p < 0.05:
        st.success("Rejeitamos H₀ → Jogos de Ação vendem significativamente mais que RPG (nível 5%).")
    else:
        st.info("Não rejeitamos H₀ → Não há evidência suficiente de que Ação venda mais que RPG.")

    # boxplot comparativo
    subset = data[data['Genre'].isin(['Action','Role-Playing'])]
    fig = px.box(subset, x='Genre', y='Global_Sales',
                 title="Distribuição de Vendas Globais: Ação vs RPG",
                 labels={'Global_Sales': 'Vendas Globais (mi)', 'Genre': 'Gênero'})
    fig.update_layout(template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)


# Teste de hipótese: Jogos antigos (até 2010) vendem mais que jogos atuais (após 2010)
def teste_jogos_antigos_vs_atuais(data: pd.DataFrame):
    st.write("**H₀**: A média de vendas globais de jogos até 2010 = média de vendas após 2010")
    st.write("**H₁**: Jogos até 2010 vendem mais (média maior)")

    antigos = data.loc[data['Year_of_Release'] <= 2010, 'Global_Sales'].dropna()
    atuais = data.loc[data['Year_of_Release'] > 2010, 'Global_Sales'].dropna()

    if antigos.empty or atuais.empty:
        st.warning("Não há dados suficientes para comparar jogos antigos e atuais.")
        return

    # teste t
    stat, p = ttest_ind(antigos, atuais, alternative='greater', equal_var=False)

    st.write(f"Estatística t: **{stat:.3f}**")
    st.write(f"P-Valor: **{p:.5f}**")
    st.write(f"Nível de Significância: **0.05 (5%)**")

    if p < 0.05:
        st.success("Rejeitamos H₀ → Jogos antigos (até 2010) vendem significativamente mais.")
    else:
        st.info("Não rejeitamos H₀ → Não há evidência suficiente de que jogos antigos vendam mais.")

    # boxplot comparativo
    subset = data[data['Year_of_Release'].notna()].copy()
    subset['Era'] = subset['Year_of_Release'].apply(lambda x: 'Até 2010' if x <= 2010 else 'Após 2010')
    fig = px.box(subset, x='Era', y='Global_Sales',
                 title="Distribuição de Vendas Globais: Jogos Antigos vs Atuais",
                 labels={'Global_Sales': 'Vendas Globais (mi)', 'Era': 'Período'})
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
        'Vendas por Classificação Etária',
        'Medidas Centrais & Distribuições',
        'Teste de Hipótese'
    ],
    index=0
)

def mostrar_dicionario_variaveis():
    data = [('Name', 'Qualitativa', 'Nominal', 'Nome do Jogo → Identificação sem Hierarquia'),
            ('Platform', 'Qualitativa', 'Nominal', 'Plataforma → Categorias sem Hierarquia'),
            ('Year_of_Release', 'Quantitativa', 'Discreta', 'Ano de Lançamento → Números Inteiros'),
            ('Genre', 'Qualitativa', 'Nominal', 'Gênero do Jogo → Categorias sem Hierarquia'),
            ('Publisher', 'Qualitativa', 'Nominal', 'Nome da Empresa Publicadora → Identificação sem Hierarquia'),
            ('Developer', 'Qualitativa', 'Nominal', 'Nome do Estúdio Desenvolvedor → Identificação sem Hierarquia'),
            ('Rating', 'Qualitativa', 'Ordinal', 'Classificação Etária (ESRB) → Classificação com Ordem Implícita'),
            ('NA_Sales', 'Quantitativa', 'Contínua', 'Vendas na América do Norte (Milhões) → Números Reais, pode ter Decimais'),
            ('EU_Sales', 'Quantitativa', 'Contínua', 'Vendas na Europa (Milhões) → Números Reais, pode ter Decimais'),
            ('JP_Sales', 'Quantitativa', 'Contínua', 'Vendas no Japão (Milhões) → Números Reais, pode ter Decimais'),
            ('Other_Sales', 'Quantitativa', 'Contínua', 'Vendas em Outras Regiões (Milhões) → Números Reais, pode ter Decimais'),
            ('Global_Sales', 'Quantitativa', 'Contínua', 'Soma das Vendas Globais (Milhões) → Números Reais, pode ter Decimais'),
            ('Critic_Score', 'Quantitativa', 'Contínua', 'Nota Média de Críticos (0–100) → Números Reais, pode ter Decimais'),
            ('Critic_Count', 'Quantitativa', 'Discreta', 'Número de Críticos → Números Inteiros'),
            ('User_Score', 'Quantitativa', 'Contínua', 'Nota Média de Usuários (0–10), → Números Reais, pode ter Decimais'),
            ('User_Count', 'Quantitativa', 'Discreta', 'Número de Usuários → Números Inteiros')]
    df_dict = pd.DataFrame(data, columns=['Coluna', 'Tipo', 'Subtipo', 'Descrição'])
    st.dataframe(df_dict, use_container_width=True)

# Switch-case para exibir a análise escolhida
match analises:
    case 'Visão Geral':
        st.subheader('📌 Visão Geral dos Dados')
        st.write('Base de dados: Vendas e Análises de Jogos *(1980 - 2020)*')
        with st.expander('Visualizar amostra da base', expanded=False):
            st.dataframe(df_f.head(25), use_container_width=True)
        st.divider()
        st.subheader('📋 Identificação dos Tipos das Variáveis & Descrição das Colunas')
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
        st.markdown('''
        - O auge dos lançamentos foi entre 2005 e 2015, chegando a um pico de 1427 jogos em 2008.
        - Após 2016 houve uma queda brusca nos registros, com pouquíssimos lançamentos em 2017 e 2020.
        Provavelmente isso se deve ao jogos estarem ficando cada vez mais caros e demorados de produzir.
        \n
        💡 **Insight:** O período de ouro do mercado foi a década de 2000, marcado pela expansão do PS2, Wii e DS.
        ''')

    case 'Gêneros Mais Populares':
        st.subheader('🎭 Gêneros Mais Populares')
        generos_populares(df_f)
        st.markdown('''
        - Ação (Action) é o gênero dominante (3.370 jogos).
        - Em seguida vêm Esportes (Sports), Misc (Party/Casual), RPGs e Shooter.
        \n
        💡 **Insight:** Jogos de ação e esportes são os mais produzidos, mas RPG e Shooters representam nichos muito fortes em vendas.
        ''')

    case 'Plataformas com Mais Lançamentos':
        st.subheader('💻 Plataformas com Mais Lançamentos')
        lancamentos_plataformas(df_f)
        st.markdown('''
        - PS2 (2161 jogos) e Nintendo DS (2152 jogos) são os campeões em número de lançamentos.
        - Seguem PS3, Wii e Xbox 360, mostrando a força da geração 2005–2013.
        \n
        💡 **Insight:** Consoles da Sony e Nintendo dominaram em quantidade de títulos.
        ''')

    case 'Top 10 Jogos por Vendas Globais':
        st.subheader('🏆 Top 10 Jogos por Vendas Globais')
        vendas_globais(df_f)
        st.markdown('''
        💡 **Insight:** O top 10 é dominado pela Nintendo, com foco em jogos casuais e familiares.
        ''')

    case 'Vendas por Região':
        st.subheader('🌍 Vendas por Região')
        vendas_regiao(df_f)
        st.markdown('''
        - América do Norte (4402M) é o maior mercado.
        - Europa (2425M) em segundo, seguida pelo Japão (1297M).
        - Outras regiões representam 791M.
        \n
        💡 **Insight:** NA é o maior consumidor de jogos, mas o Japão se destaca em exclusivos e gêneros específicos (RPGs, por exemplo).
        ''')

    case 'Notas: Críticos vs Usuários':
        st.subheader('⭐ Correlação de Notas: Críticos vs Usuários')
        correlacao_notas(df_f)
        st.markdown('''
        - Correlação = 0.58 (moderada positiva).
        \n
        💡 **Insight:** Jogos bem avaliados pela crítica tendem a agradar os jogadores também, 
        mas há discrepâncias (nem sempre o que a crítica gosta é o que os jogadores compram).
        ''')

    case 'Vendas por Classificação Etária':
        st.subheader('🔞 Vendas por Classificação Etária')
        vendas_classificacao_etaria(df_f)
        st.markdown('''
        - E (Everyone) lidera com 2437M vendas globais.
        - Seguem T (Teen) com 1494M e M (Mature) com 1474M.
        - Ratings menores (E10+, AO, EC) têm pouco impacto.
        \n
        💡 **Insight:** Jogos para todas as idades (E) dominam em vendas, confirmando o apelo familiar, mas T e M também têm grande mercado.
        ''')

    case 'Medidas Centrais & Distribuições':
        st.subheader('📊 Medidas Centrais e Distribuições')
        medidas_centrais(df_f)

    case 'Teste de Hipótese':
        st.subheader('🎮 Teste de Hipótese: Ação vs RPG')
        teste_acao_vs_rpg(df_f)
        st.divider()
        st.subheader('🎮 Teste de Hipótese: Jogos Antigos (até 2010) vs Atuais (após 2010)')
        teste_jogos_antigos_vs_atuais(df_f)

    case _:
        st.warning('Selecione uma análise válida na barra lateral.')
