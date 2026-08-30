import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

# Configuração da Página
st.set_page_config(
    page_title="Vexys Capital | Simulador de Resiliência Monetária",
    page_icon="📊",
    layout="wide"
)

# Título Principal
st.title("Vexys Capital — Simulador de Resiliência Monetária (30 Anos)")
st.markdown("### Avalie o impacto estrutural da inflação e da dominância fiscal sobre o seu patrimônio.")

# Função para buscar dados atualizados (Exemplo integrando com Supabase ou Fallback estático)
@st.cache_data(ttl=3600)
def carregar_dados_moedas():
    # Aqui o Streamlit pode buscar a tabela atualizada pelo n8n no Supabase
    # Se preferir manter o dicionário base estruturado enquanto integra o n8n, usamos a base robusta abaixo:
    return {
        "USD": {"nome": "Dólar Americano", "bloco": "Estados Unidos", "tier": "Tier 1 - Reserva Global", "inflacao_base": 2.5, "f_esc": 1.0, "div_pib": 120.0},
        "EUR": {"nome": "Euro", "bloco": "Zona do Euro", "tier": "Tier 1 - Reserva Global", "inflacao_base": 2.4, "f_esc": 0.9, "div_pib": 90.0},
        "CNY": {"nome": "Yuan / Renminbi Chinês", "bloco": "China", "tier": "Tier 1 - Superpotência Comercial", "inflacao_base": 2.0, "f_esc": 0.7, "div_pib": 83.0},
        "JPY": {"nome": "Iene Japonês", "bloco": "Japão", "tier": "Tier 1 - Liquidez Estável", "inflacao_base": 1.5, "f_esc": 0.6, "div_pib": 260.0},
        "GBP": {"nome": "Libra Esterlina", "bloco": "Reino Unido", "tier": "Tier 1 - Reserva Global", "inflacao_base": 2.8, "f_esc": 0.8, "div_pib": 100.0},
        "CHF": {"nome": "Franco Suíço", "bloco": "Suíça", "tier": "Tier 1 - Alta Solidez", "inflacao_base": 1.2, "f_esc": 0.85, "div_pib": 42.0},
        "CAD": {"nome": "Dólar Canadense", "bloco": "Canadá", "tier": "Tier 2 - Commodities / Energia", "inflacao_base": 2.6, "f_esc": 0.5, "div_pib": 107.0},
        "AUD": {"nome": "Dólar Australiano", "bloco": "Austrália", "tier": "Tier 2 - Commodities / Ásia", "inflacao_base": 3.0, "f_esc": 0.45, "div_pib": 55.0},
        "SGD": {"nome": "Dólar de Singapura", "bloco": "Singapura", "tier": "Tier 2 - Hub Financeiro", "inflacao_base": 2.2, "f_esc": 0.5, "div_pib": 160.0},
        "INR": {"nome": "Rúpia Indiana", "bloco": "Índia", "tier": "Tier 2 - Crescimento Demográfico", "inflacao_base": 5.0, "f_esc": 0.2, "div_pib": 85.0},
        "BRL": {"nome": "Real Brasileiro", "bloco": "Brasil", "tier": "Tier 3 - Sensível / Emergente", "inflacao_base": 4.5, "f_esc": 0.15, "div_pib": 78.0},
        "MXN": {"nome": "Peso Mexicano", "bloco": "México", "tier": "Tier 3 - Nearshoring / Sensível", "inflacao_base": 4.2, "f_esc": 0.18, "div_pib": 50.0},
        "CLP": {"nome": "Peso Chileno", "bloco": "Chile", "tier": "Tier 3 - Cobre / Regional", "inflacao_base": 3.8, "f_esc": 0.12, "div_pib": 38.0},
        "ZAR": {"nome": "Rand Sul-Africano", "bloco": "África do Sul", "tier": "Tier 3 - Minerais Críticos", "inflacao_base": 5.2, "f_esc": 0.10, "div_pib": 73.0},
        "ARS": {"nome": "Peso Argentino", "bloco": "Argentina", "tier": "Tier 4 - Crítico / Dominância Fiscal", "inflacao_base": 45.0, "f_esc": 0.01, "div_pib": 85.0}
    }

moedas_dict = carregar_dados_moedas()