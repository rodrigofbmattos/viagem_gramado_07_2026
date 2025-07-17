#
# Aplicação Streamlit para o planejamento orçamentário para a viagem para Gramado em Julho de 2026
#

import streamlit as st
import pandas as pd
import re # Para extrair o nome do item da string de seleção

# --- Configurações da Página ---
st.set_page_config(layout="wide", page_title="Meu Planejador de Viagens Personalizado")

st.title("✈️ Planejador de Orçamento de Viagem Personalizado")
st.markdown("Use os menus laterais para selecionar o hotel e o carro, e veja o custo total da sua viagem!")

# --- Caminho para o arquivo Excel ---
excel_file_path = 'Viagem.xlsx'

# --- Função para Carregar os Dados do Excel (com cache para performance) ---
@st.cache_data
def load_excel_data(file_path):
    try:
        df_hoteis = pd.read_excel(file_path, sheet_name='Hotéis')
        df_aluguel_carro = pd.read_excel(file_path, sheet_name='Aluguel de Carro')
        df_atracoes = pd.read_excel(file_path, sheet_name='Atrações')
        # A aba 'Total' é calculada no próprio Streamlit, não a lemos diretamente para cálculos
        return df_hoteis, df_aluguel_carro, df_atracoes
    except FileNotFoundError:
        st.error(f"Erro: O arquivo '{file_path}' não foi encontrado. Por favor, certifique-se de que ele está na mesma pasta que este script.")
        st.stop()
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo Excel: {e}")
        st.stop()

# Carregar os DataFrames
df_hoteis_original, df_aluguel_carro_original, df_atracoes_original = load_excel_data(excel_file_path)

# --- Processamento dos Dados para Seleções ---

# Hotéis: As opções para o selectbox devem ser formatadas
# Excluímos a última linha que é a de seleção no Excel
hotel_options_for_display = [
    f"{row['Nome do Hotel']} (R$ {row['Preço por Período (R$)']:.2f})"
    for _, row in df_hoteis_original.iloc[:-1].iterrows() # Ignora a linha de seleção final do Excel
]
hotel_options_for_display.insert(0, "--- Selecione um Hotel ---") # Opção padrão

# Aluguel de Carro: As opções para o selectbox devem ser formatadas
# Excluímos a última linha que é a de seleção no Excel
carro_options_for_display = [
    f"{row['Tipo do Carro']} - {row['Locadora']} (R$ {row['Preço por Período (R$)']:.2f})"
    for _, row in df_aluguel_carro_original.iloc[:-1].iterrows() # Ignora a linha de seleção final do Excel
]
carro_options_for_display.insert(0, "--- Selecione um Carro ---") # Opção padrão

# Total de Atrações: Buscamos a soma que está na aba Atrações
# Localizamos a linha onde a coluna 'Atrações' contém 'Total Atrações'
total_atracoes_value = 0.0
total_atracoes_row = df_atracoes_original[df_atracoes_original['Atrações'] == 'Total Atrações']
if not total_atracoes_row.empty:
    total_atracoes_value = total_atracoes_row['Valor (R$)'].iloc[0]
else: # Fallback caso a linha de total não seja encontrada (soma as atrações diretamente)
    total_atracoes_value = df_atracoes_original.iloc[:-1]['Valor (R$)'].sum() # Soma tudo menos a linha final de total


# --- Layout da Interface Streamlit ---

st.sidebar.header("Opções de Seleção")

# --- Seleção de Hotel ---
st.subheader("🏨 1. Escolha o Hotel")
selected_hotel_display = st.sidebar.selectbox(
    "Selecione o Hotel:",
    options=hotel_options_for_display,
    index=0 # Opção padrão
)

current_hotel_price = 0.0
if selected_hotel_display != "--- Selecione um Hotel ---":
    # Extrai o nome do hotel da string selecionada (tudo antes de " (R$")
    match_hotel = re.match(r"(.+)\s\(R\$\s[\d,\.]+\)", selected_hotel_display)
    if match_hotel:
        hotel_name_clean = match_hotel.group(1)
        # Busca o preço no DataFrame original (excluindo a linha de seleção)
        hotel_row_data = df_hoteis_original[df_hoteis_original['Nome do Hotel'] == hotel_name_clean].iloc[0]
        current_hotel_price = hotel_row_data['Preço por Período (R$)']
        st.info(f"**Hotel Selecionado:** {hotel_name_clean} - **R$ {current_hotel_price:.2f}**")
    else:
        st.warning("Formato de seleção de hotel inválido.")
else:
    st.info("Nenhum hotel selecionado. Selecione um para incluir no cálculo total.")

st.markdown("---")

# --- Custos de Atrações (Fixos) ---
st.subheader("💸 2. Custos de Atrações (Fixos)")
# Exibe a tabela de atrações (excluindo a linha do total)
st.dataframe(df_atracoes_original.iloc[:-1].style.format({"Valor (R$)": "R$ {:,.2f}"}), hide_index=True, use_container_width=True)
st.write(f"**Total de Custos de Atrações Fixos:** **R$ {total_atracoes_value:.2f}**")

st.markdown("---")

# --- Seleção de Aluguel de Carro ---
st.subheader("🚗 3. Escolha o Aluguel de Carro")
selected_carro_display = st.sidebar.selectbox(
    "Selecione o Aluguel de Carro:",
    options=carro_options_for_display,
    index=0 # Opção padrão
)

current_carro_price = 0.0
if selected_carro_display != "--- Selecione um Carro ---":
    # Extrai a descrição do carro da string selecionada (tudo antes de " (R$")
    match_carro = re.match(r"(.+)\s\(R\$\s[\d,\.]+\)", selected_carro_display)
    if match_carro:
        carro_description_clean = match_carro.group(1)
        # Busca o preço no DataFrame original
        carro_row_data = df_aluguel_carro_original[
            (df_aluguel_carro_original['Tipo do Carro'] + ' - ' + df_aluguel_carro_original['Locadora']) == carro_description_clean
        ].iloc[0]
        current_carro_price = carro_row_data['Preço por Período (R$)']
        st.info(f"**Aluguel de Carro Selecionado:** {carro_description_clean} - **R$ {current_carro_price:.2f}**")
    else:
        st.warning("Formato de seleção de carro inválido.")
else:
    st.info("Nenhum aluguel de carro selecionado. Selecione um para incluir no cálculo total.")

st.markdown("---")

# --- Cálculo e Exibição do Custo Total da Viagem ---
st.header("💰 Custo Total Estimado da Viagem")

final_total_cost = current_hotel_price + total_atracoes_value + current_carro_price

st.success(f"**O Custo Total Estimado da Sua Viagem é: R$ {final_total_cost:.2f}**")

# --- Estilos CSS personalizados (opcional) ---
st.markdown("""
<style>
    .st-emotion-cache-1r6dm7m { /* Target sidebar header */
        color: #FF4B4B; /* Streamlit's primary red for emphasis */
    }
    .st-emotion-cache-10qnzpf p { /* Target text in st.write, st.info */
        font-size: 1.1em;
    }
    .st-emotion-cache-nahz7x { /* Target st.success message box */
        background-color: #e6ffe6; /* Light green background */
        border-color: #66cc66; /* Darker green border */
        color: #338833; /* Dark green text */
    }
    .st-emotion-cache-nahz7x p {
        font-size: 1.3em;
        font-weight: bold;
    }
    /* Estilo para tabelas */
    .dataframe {
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)