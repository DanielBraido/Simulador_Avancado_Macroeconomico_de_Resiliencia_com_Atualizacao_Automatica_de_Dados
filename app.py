import streamlit as st
from supabase import create_client, Client
import pandas as st_pandas

# Configuração inicial da página
st.set_page_config(page_title="Vexys Capital - Simulador", layout="wide")

# Títulos
st.title("Vexys Capital — Simulador de Resiliência Monetária (30 Anos)")
st.markdown("Avalie o impacto estrutural da inflação e da dominância fiscal sobre o seu patrimônio.")
st.divider()

# Conexão com o Supabase usando os Secrets do Streamlit
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_connection()

# Busca dos dados no banco
@st.cache_data(ttl=3600) # Atualiza o cache a cada 1 hora
def fetch_data():
    resposta = supabase.table("vexys_indicadores_moedas").select("*").execute()
    return resposta.data

# Executa a busca e exibe na tela
try:
    dados_moedas = fetch_data()
    
    if dados_moedas:
        st.success("Conexão com o banco de dados estabelecida com sucesso!")
        st.subheader("Indicadores Macroeconômicos Globais (Ao Vivo)")
        
        # Transforma os dados em uma tabela visual (DataFrame)
        st.dataframe(dados_moedas, use_container_width=True)
    else:
        st.warning("O banco de dados está conectado, mas a tabela está vazia.")

except Exception as e:
    st.error(f"Erro ao conectar com o banco de dados: {e}")
