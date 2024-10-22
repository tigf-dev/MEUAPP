import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
from dotenv import load_dotenv

# --- Carregar variáveis de ambiente do arquivo .env ---
load_dotenv()

# --- Configuração da API Google Sheets ---
scope = [
    "https://spreadsheets.google.com/feeds", 
    "https://www.googleapis.com/auth/spreadsheets"
]

# Obter as credenciais do ambiente
google_credentials = os.getenv('GOOGLE_CREDENTIALS')
creds_dict = json.loads(google_credentials)  # Converter de string para dict
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# --- Carrega os dados da planilha ---
spreadsheet = client.open_by_url(
    "https://docs.google.com/spreadsheets/d/1AZ2K-U1i-zyEeqsk42MQzBbrxxNhIPEEhFQ000kouqI/edit?gid=0#gid=0"
)
worksheet = spreadsheet.worksheet("COLMEIA")
data = worksheet.get_all_records()

# Criação do DataFrame
df = pd.DataFrame(data)

# --- Exibir a planilha completa ---
st.markdown("<h1 style='text-align: center;'>Sistema de Estoque - Mapeamento de Colmeias</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center;'>Visualização Completa da Planilha</h2>", unsafe_allow_html=True)

# Usar use_container_width=True para ocupar toda a largura disponível
st.dataframe(df, use_container_width=True)

# --- Tabela estilo Batalha Naval ---
st.markdown("<h2 style='text-align: center;'>Visualização Estilo Batalha Naval</h2>", unsafe_allow_html=True)

# Criar uma tabela para a visualização estilo Batalha Naval
colmeias = df['Localização colmeia'].unique()  # Colunas são as localizações das colmeias
espacos = df['Localização espaços'].unique()  # Linhas são os espaços

# Criação da tabela de batalha naval
tabela_batalha = pd.DataFrame(index=espacos, columns=colmeias)

# Preencher a tabela com HTML de tooltip ou "Vazio"
for _, row in df.iterrows():
    col = row['Localização colmeia']
    row_idx = row['Localização espaços']
    if col in tabela_batalha.columns and row_idx in tabela_batalha.index:
        if row['Descrição'] and row['Quantidade'] > 0:
            descricao = f"{row['Descrição']} ({row['Quantidade']})"
            tooltip_html = f"""
                <div class="tooltip">
                    <span class="tooltiptext">{descricao}</span>
                    Peça Oculta
                </div>
            """
            # Se a célula estiver vazia ou contiver "Vazio", adicione o tooltip_html
            if pd.isna(tabela_batalha.at[row_idx, col]) or tabela_batalha.at[row_idx, col] == "Vazio":
                tabela_batalha.at[row_idx, col] = tooltip_html
            else:
                # Concatenar se já houver um valor
                tabela_batalha.at[row_idx, col] += f"<br>{tooltip_html}"
        else:
            tabela_batalha.at[row_idx, col] = "Vazio"

# Substituir "\n" por "" (nada) e manter "Vazio" como está
tabela_batalha.replace("\n", "", regex=True, inplace=True)

# --- Estilo CSS para o tooltip e centralização ---
st.markdown("""
    <style>
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: pointer;
        border-bottom: 1px dotted black;
        color: transparent; /* Torna o texto "Peça Oculta" invisível */
    }

    .tooltip .tooltiptext {
        visibility: hidden;
        width: 160px;
        background-color: black;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;  /* Posição acima do texto */
        left: 50%;
        margin-left: -80px;
        opacity: 0;
        transition: opacity 0.3s;
    }

    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }

    /* Centralizar a tabela */
    .tabela-centralizada {
        display: flex;
        justify-content: center;
    }

    /* Centralizar o texto nas células da tabela */
    table {
        margin: 0 auto; /* Centraliza a tabela na página */
        border-collapse: collapse; /* Remove espaços entre as células */
    }
    th, td {
        text-align: center; /* Centraliza o texto das células */
        padding: 10px; /* Adiciona espaço interno nas células */
        border: 1px solid black; /* Adiciona bordas às células */
    }
    </style>
""", unsafe_allow_html=True)

# Exibir a tabela de batalha naval com HTML seguro, dentro de um container centralizado
st.markdown(
    f'<div class="tabela-centralizada">{tabela_batalha.to_html(escape=False)}</div>',
    unsafe_allow_html=True
)
