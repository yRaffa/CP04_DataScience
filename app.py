import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title='Portfólio Profissional', page_icon='🎮', layout='wide')

st.title('🎮 Portfólio Profissional - Rafael Oliveira')
st.subheader('Apresentação Profissional e Análise de Dados')

tabs = st.tabs(['👤 Introdução Pessoal', '🎓 Formação & Experiências', '🛠️ Skills'])

# Introdução Pessoal
with tabs[0]:
    st.header('👤 Introdução Pessoal')
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image('./img/rafael.jpg', caption='Rafael Oliveira', width=180)
    with col2:
        st.subheader('Olá, eu sou Rafael Federici de Oliveira! 👋')
        st.write('''
            Atualmente estou cursando **Engenharia de Software na FIAP**.
            
            Sou apaixonado por tecnologia, inovação e especialmente pelo **desenvolvimento de jogos**.

            Em meus estudos, estou focado em aprimorar minhas habilidades em **Python, Modelagem 3D e Game Engines (Unity/Unreal/GameMaker)**.
                 
            Sonho em trabalhar na indústria de jogos, criando e desenvolvendo experiências imersivas e envolventes. 
            Meu objetivo é unir **programação, criatividade e entretenimento** para fazer experiências digitais únicas.
            ''')

# Formação e Experiências
with tabs[1]:
    st.header('🎓 Formações e Experiências')

    st.subheader('🎓 Formação Acadêmica')
    st.write('- **Engenharia de Software - FIAP** *(2024 - 2027)*')

    st.subheader('📚 Outras Formações e Cursos')
    st.write('''
             - **Técnico em Informática - ETEC Parque da Juventude** *(2018 - 2020)*
             - **Desenvolvimento Android (Kotlin) - Escola de Programação MadCode** *(2019)*
             - **Curso de Inglês - WiseUp** *(2017 - 2021)*
             - **Cursos de Programação e GameDev - Alura** *(2020 - Atualmente)*
             - **Cursos Extra Curriculares - FIAP Nano Courses** *(2024 - Atualmente)*
             - **Engenharia da Computação - UNIFESP** *(2022 - 2023, pendente)*
             ''')
    
    st.subheader('📕 Projetos Acadêmicos')
    st.write('''
        - **FIAP Global Solution e CHALLENGE**: Projetos de desenvolvimento de soluções integradas, 
        envolvendo Python, Banco de Dados, Front-End, Data Science, AR/VR, etc.  
        - **Projetos de Programação**: Sistemas em Python e Java aplicados a problemas reais.  
        ''')

    st.subheader('💼 Experiências')
    st.write('''
        - Participação em equipes multidisciplinares com metodologias ágeis (Scrum, Kanban).  
        - Automação de processos em tarefas profissionais.
        - Desenvolvimento de protótipos de jogos.
        ''')

# Skills
with tabs[2]:
    st.header('🛠️ Minhas Skills')

    st.subheader('Principais Habilidades 🔎')

    skills = {
        'Programação': 95,
        'Desenvolvimento Web': 75,
        'Desenvolvimento de Jogos': 70,
        'Análise de Dados': 75,
        'Inglês': 90,
        'Trabalho em Equipe': 85,
        'Proatividade': 80,
        'Criatividade': 75,
        'Metodologias Ágeis': 60
    }

    col1, col2 = st.columns(2)

    # Radar Chart
    with col1:
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=list(skills.values()),
            theta=list(skills.keys()),
            fill='toself',
            name='Habilidades',
            line=dict(color='purple')
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=False, range=[0, 100])
            ),
            showlegend=False,
            template='plotly_dark',
            title='Minhas Estatísticas'
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # Gráfico de Barras
    with col2:
        df_skills = pd.DataFrame({
            'Skill': list(skills.keys()),
            'Nível': list(skills.values())
        })
        fig_bar = px.bar(
            df_skills,
            x='Skill',
            y='Nível',
            text='Nível',
            color='Skill',
            color_discrete_sequence=['#636EFA', '#EF553B', '#00CC96', '#AB63FA']
        )
        fig_bar.update_traces(textposition='outside')
        fig_bar.update_layout(
            title='Comparação de Habilidades',
            yaxis=dict(range=[0, 100]),
            template='plotly_dark'
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader('Hard Skills 🧠')
    st.write('''
        - Programação **(Python, C, Java)** - *Avançado*
        - Desenvolvimento Web **(HTML, CSS, JavaScript)** - *Avançado*
        - Desenvolvimento de Jogos **(Unity, Unreal, GameMaker)** - *Intermediário*
        - Modelagem 3D **(Maya)** - *Intermediário*
        - Banco de Dados **(SQL)** - *Intermediário*
        - Análise e Visualização de Dados **(Pandas, Matplotlib, Seaborn)** - *Intermediário*
        - Inglês Fluente **(Leitura, Escrita, Conversação)** - *Avançado*
        ''')

    st.subheader('Soft Skills 💭')
    st.write('''
        - Trabalho em equipe 🤝
        - Proatividade 🚀
        - Criatividade 🎨
        - Resolução de problemas 🧩
        ''')
    
    st.subheader('Ferramentas & Metodologias 🔧')
    st.write('''
        - Metodologias Ágeis (Scrum, Kanban)  
        - Git / GitHub  
        - Excel  
        ''')
