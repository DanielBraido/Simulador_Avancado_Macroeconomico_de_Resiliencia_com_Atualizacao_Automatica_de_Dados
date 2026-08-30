import streamlit as st
from supabase import create_client, Client
import pandas as pd
import numpy as np
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Vexys Capital — Simulador de Resiliência Monetária", layout="wide")

# Conexão com o Supabase usando os Secrets
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_connection()

# Busca dos dados de inflação atualizados pelo n8n
@st.cache_data(ttl=3600)
def fetch_data():
    resposta = supabase.table("vexys_indicadores_moedas").select("*").execute()
    return resposta.data

dados_brutos = fetch_data()
df_dados = pd.DataFrame(dados_brutos) if dados_brutos else pd.DataFrame()

# Tratamento para garantir dados únicos e válidos
if not df_dados.empty:
    if 'id' in df_dados.columns:
        df_dados = df_dados.sort_values(by='id', ascending=False)
    df_dados = df_dados.drop_duplicates(subset=['nome_moeda'], keep='first')
    df_dados = df_dados[df_dados['inflacao_base'] > 0]

# Cabeçalho Principal
st.title("Vexys Capital — Simulador de Resiliência Monetária (30 Anos)")
st.markdown("Avalie o impacto estrutural da inflação e da dominância fiscal sobre o seu patrimônio.")
st.divider()

# Barra lateral para os parâmetros
st.sidebar.header("Parâmetros da Simulação")

anos_simulacao = st.sidebar.slider("Horizonte de Tempo (Anos)", min_value=1, max_value=50, value=30)
patrimonio_inicial = st.sidebar.number_input("Patrimônio Inicial (R$)", value=100000.0, step=10000.0)

st.sidebar.subheader("Seleção de Moedas / Países")
if not df_dados.empty and 'nome_moeda' in df_dados.columns:
    opcoes_moedas = df_dados['nome_moeda'].unique().tolist()
    moedas_selecionadas = st.sidebar.multiselect("Escolha para comparar:", options=opcoes_moedas, default=opcoes_moedas[:5] if len(opcoes_moedas) >= 5 else opcoes_moedas)
else:
    moedas_selecionadas = []
    st.sidebar.warning("Carregando moedas do banco...")

# Corpo Principal: Gráfico e Pódio Aprimorado
if moedas_selecionadas and not df_dados.empty:
    st.subheader("Evolução do Poder de Compra Corroído pela Inflação")
    
    anos = np.arange(0, anos_simulacao + 1)
    dados_grafico = []
    resumo_final = []
    
    for moeda in moedas_selecionadas:
        inflacao_row = df_dados[df_dados['nome_moeda'] == moeda]
        if not inflacao_row.empty:
            taxa_inflacao = float(inflacao_row['inflacao_base'].values[0]) / 100.0
        else:
            taxa_inflacao = 0.05
            
        # Fórmula de desvalorização do poder de compra
        poder_compra = patrimonio_inicial * (1 / (1 + taxa_inflacao) ** anos)
        
        for ano, valor in zip(anos, poder_compra):
            dados_grafico.append({
                "Ano": ano,
                "Poder de Compra (R$)": valor,
                "Moeda / País": moeda
            })
            
        patrimonio_final = poder_compra[-1]
        
        # Cálculo das porcentagens de restante e perda
        pct_restante = (patrimonio_final / patrimonio_inicial) * 100
        pct_perda = 100 - pct_restante
        
        resumo_final.append({
            "Moeda / País": moeda, 
            "Patrimônio Final Restante (R$)": patrimonio_final,
            "% Restante": pct_restante,
            "% de Perda (Corrosão)": pct_perda,
            "Inflação Base (%)": taxa_inflacao * 100
        })

    # Gráfico Plotly
    df_plot = pd.DataFrame(dados_grafico)
    fig = px.line(
        df_plot, 
        x="Ano", 
        y="Poder de Compra (R$)", 
        color="Moeda / País",
        markers=False,
        height=500
    )
    fig.update_layout(
        xaxis_title="Anos de Simulação",
        yaxis_title="Poder de Compra Restante (R$)",
        legend_title="Países",
        template="plotly_dark"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()

    # Seção do Ranking com Medalhas e Porcentagens
    st.subheader("🏆 Pódio de Resiliência Monetária (Menor Corrosão)")
    
    df_ranking = pd.DataFrame(resumo_final)
    df_ranking = df_ranking.sort_values(by="Patrimônio Final Restante (R$)", ascending=False).reset_index(drop=True)
    
    def atribuir_medalha(posicao):
        if posicao == 0:
            return "🥇 Ouro (Campeã da Resiliência)"
        elif posicao == 1:
            return "🥈 Prata (Vice-campeã)"
        elif posicao == 2:
            return "🥉 Bronze (No Pódio)"
        else:
            return f"🛡️ {posicao + 1}º Lugar"

    df_ranking["Classificação"] = [atribuir_medalha(i) for i in range(len(df_ranking))]
    
    # Organização das colunas na tabela final
    df_ranking_exibicao = df_ranking[[
        "Classificação", 
        "Moeda / País", 
        "Patrimônio Final Restante (R$)", 
        "% Restante", 
        "% de Perda (Corrosão)", 
        "Inflação Base (%)"
    ]]
    
    st.dataframe(df_ranking_exibicao.style.format({
        "Patrimônio Final Restante (R$)": "R$ {:,.2f}",
        "% Restante": "{:.2f}%",
        "% de Perda (Corrosão)": "{:.2f}%",
        "Inflação Base (%)": "{:.2f}%"
    }), use_container_width=True)

    st.markdown("---")
    st.subheader("Dados Únicos Utilizados na Base")
    st.dataframe(df_dados[['ticker', 'nome_moeda', 'inflacao_base', 'atualizado_em']], use_container_width=True)

else:
    st.info("Selecione ao menos uma moeda na barra lateral para gerar o gráfico e o ranking.")
