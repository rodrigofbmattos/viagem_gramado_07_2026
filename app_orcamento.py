import streamlit as st
import pandas as pd
import re
import io
import locale

try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR')  # Windows fallback
    except:
        st.warning("⚠️ Não foi possível definir o locale para pt_BR.")

# Função para formatar moeda em pt_BR
def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
# --- Configurações da Página ---
st.set_page_config(layout="wide", page_title="Meu Planejador de Viagens Personalizado V20") # Updated version number

st.title("✈️ Planejador de Orçamento de Viagem Personalizado")

# Inicializa variáveis de sessão para evitar erros de acesso e prevenir avisos
if 'selected_hotel_name' not in st.session_state:
    st.session_state.selected_hotel_name = None
    
if 'selected_carro_type_locadora' not in st.session_state:
    st.session_state.selected_carro_type_locadora = None
    
if 'selected_passagem_ida' not in st.session_state:
    st.session_state.selected_passagem_ida = None

if 'selected_passagem_volta' not in st.session_state:
    st.session_state.selected_passagem_volta = None

st.markdown("Ajuste as opções para ver o custo total da sua viagem!")

# --- Caminho para o arquivo Excel (apenas para referência, pois os dados estão embutidos) ---
excel_file_path = 'Viagem.xlsx'

# --- Função para Carregar os Dados (com cache para performance) ---
@st.cache_data
def load_excel_data(file_path):
    try:
        df_hoteis = pd.read_excel(file_path, sheet_name="Hotéis").iloc[:-2]
        df_aluguel_carro = pd.read_excel(file_path, sheet_name="Aluguel de Carro").iloc[:-2]
        df_atracoes = pd.read_excel(file_path, sheet_name="Atrações").iloc[:-2]
        df_passagens = pd.read_excel(file_path, sheet_name="Passagens").iloc[:-5]

        df_hoteis.fillna({
            'Preço por Período (R$)': 0,
            'Hóspedes': 1,
            'Preço por Hóspede (R$)': 0,
            'Distância do Centro (km)': 0,
            'Chegada': pd.NaT,
            'Partida': pd.NaT,
            'Tipo do Preço': ''
        }, inplace=True)
        df_aluguel_carro.fillna({'Preço por Dia (R$)': 0, 'Dias': 1, 'Passageiros': 1, 'Preço por Período (R$)': 0, 'Preço por Passageiro (R$)': 0}, inplace=True)
        df_atracoes.fillna({'Quantidade': 0, 'Valor (R$)': 0, 'Valor Total (R$)': 0}, inplace=True)
        df_passagens.fillna({'Preço (R$)': 0, 'Preço da Bagagem (R$)': 0, 'Total (R$)': 0}, inplace=True)

        df_hoteis['Preço por Período (R$)'] = df_hoteis['Preço por Período (R$)'].astype(float)
        df_hoteis['Hóspedes'] = df_hoteis['Hóspedes'].astype(int)
        df_hoteis['Preço por Hóspede (R$)'] = df_hoteis['Preço por Hóspede (R$)'].astype(float)
        df_hoteis['Distância do Centro (km)'] = df_hoteis['Distância do Centro (km)'].astype(float)
        df_hoteis['Chegada'] = pd.to_datetime(df_hoteis['Chegada'], errors='coerce')
        df_hoteis['Partida'] = pd.to_datetime(df_hoteis['Partida'], errors='coerce')
        df_hoteis['Tipo do Preço'] = df_hoteis['Tipo do Preço'].astype(str)

        df_aluguel_carro['Preço por Dia (R$)'] = df_aluguel_carro['Preço por Dia (R$)'].astype(float)
        df_aluguel_carro['Dias'] = df_aluguel_carro['Dias'].astype(int)
        df_aluguel_carro['Passageiros'] = df_aluguel_carro['Passageiros'].astype(int)
        df_aluguel_carro['Preço por Período (R$)'] = df_aluguel_carro['Preço por Período (R$)'].astype(float)
        df_aluguel_carro['Preço por Passageiro (R$)'] = df_aluguel_carro['Preço por Passageiro (R$)'].astype(float)

        df_atracoes['Quantidade'] = df_atracoes['Quantidade'].astype(int)
        df_atracoes['Valor (R$)'] = df_atracoes['Valor (R$)'].astype(float)
        df_atracoes['Valor Total (R$)'] = df_atracoes['Valor Total (R$)'].astype(float)

        df_passagens['Preço (R$)'] = df_passagens['Preço (R$)'].astype(float)
        df_passagens['Preço da Bagagem (R$)'] = df_passagens['Preço da Bagagem (R$)'].astype(float)
        df_passagens['Total (R$)'] = df_passagens['Total (R$)'].astype(float)

        return df_hoteis, df_aluguel_carro, df_atracoes, df_passagens

    except Exception as e:
        st.error(f"Erro ao carregar os dados do Excel: {e}")
        st.stop()

# Carregar os DataFrames
df_hoteis_original, df_aluguel_carro_original, df_atracoes_original, df_passagens_original = load_excel_data(excel_file_path)

# --- Funções para lidar com a seleção e forçar rerun ---
def select_hotel(hotel_name):
    st.session_state.selected_hotel_name = hotel_name

def select_carro(carro_type, locadora):
    st.session_state.selected_carro_type_locadora = (carro_type, locadora)

def select_passagem_ida(passagem_info):
    st.session_state.selected_passagem_ida = passagem_info

def select_passagem_volta(passagem_info):
    st.session_state.selected_passagem_volta = passagem_info

# Dicionário para traduzir dias da semana
weekday_ptbr = {
    'Monday': 'segunda-feira',
    'Tuesday': 'terça-feira',
    'Wednesday': 'quarta-feira',
    'Thursday': 'quinta-feira',
    'Friday': 'sexta-feira',
    'Saturday': 'sábado',
    'Sunday': 'domingo'
}

# --- O restante do script permanece exatamente o mesmo ---

# --- Inicialização do Session State para seleções ---
# st.session_state é usado para persistir dados através das reruns do Streamlit
if 'selected_hotel_name' not in st.session_state:
    st.session_state.selected_hotel_name = None # Armazenará o nome do hotel selecionado

if 'selected_carro_type_locadora' not in st.session_state:
    st.session_state.selected_carro_type_locadora = None # Armazenará (Tipo, Locadora)

if 'selected_passagem_ida' not in st.session_state:
    st.session_state.selected_passagem_ida = None # Armazenará o sentido + companhia + origem + destino da ida

if 'selected_passagem_volta' not in st.session_state:
    st.session_state.selected_passagem_volta = None # Armazenará o sentido + companhia + origem + destino da volta

# Variáveis para armazenar os preços atuais
current_hotel_price = 0.0
current_carro_price = 0.0
total_atracoes_calculado = 0.0
current_passagem_ida_price = 0.0
current_passagem_volta_price = 0.0

# --- Layout da Interface Streamlit ---

# Sidebar Navigation (antes de calcular o custo total)
st.sidebar.markdown("### Navegação")
st.sidebar.markdown("- [Início](#planejador-de-orçamento-de-viagem-personalizado)")
st.sidebar.markdown("- [Escolha o Hotel](#1-escolha-o-hotel)")
st.sidebar.markdown("- [Escolha as Passagens Aéreas](#2-escolha-as-passagens-aéreas)") # New section in sidebar
st.sidebar.markdown("- [Ajuste as Quantidades das Atrações](#3-ajuste-as-quantidades-das-atrações)")
st.sidebar.markdown("- [Escolha o Aluguel de Carro](#4-escolha-o-aluguel-de-carro)")

# --- 1. Seleção de Hotel (em blocos com botão de seleção) ---
st.subheader("🏨 1. Escolha o Hotel")
st.write("Selecione um hotel da lista abaixo:")

# Criar colunas para os blocos de hotel
cols_per_row = 3
# Para garantir que as colunas sejam criadas corretamente, especialmente se o número de itens não for múltiplo de cols_per_row
# podemos criar todas as colunas de uma vez e depois preenchê-las
hotel_blocks_container = st.container() # Cria um container para as colunas de hotéis
with hotel_blocks_container:
    hotel_cols = st.columns(cols_per_row) # Cria uma lista de objetos de coluna

# Itera sobre cada hotel para criar um bloco de seleção dentro de uma coluna
for index, row in df_hoteis_original.iterrows():
    hotel_name = row['Nome do Hotel']
    is_selected = (st.session_state.selected_hotel_name == hotel_name)

    # Usa o índice para determinar em qual coluna o bloco será colocado
    with hotel_cols[index % cols_per_row]:
        # st.container cria um bloco visualmente separado
        with st.container(border=True):
            # Título do hotel no bloco
            st.markdown(f"**{row['Nome do Hotel']}**") # Título maior para o nome do hotel
            st.write(f"- **Preço p/ Período:** {formatar_moeda(row['Preço por Período (R$)'])}")
            st.write(f"- **Hóspedes:** {row['Hóspedes']}")
            st.write(f"- **Preço p/ Hóspede:** {formatar_moeda(row['Preço por Hóspede (R$)'])}")
            st.write(f"- **Distância Centro:** {row['Distância do Centro (km)']:.1f} km")
            
            if pd.notnull(row['Chegada']):
                dia_semana = row['Chegada'].day_name()
                dia_semana_pt = weekday_ptbr.get(dia_semana, '')
                st.write(f"- **Chegada:** {dia_semana_pt}, {row['Chegada'].strftime('%d/%m/%Y')}")
            else:
                st.write("Chegada: -")
                
            if pd.notnull(row['Partida']):
                dia_semana_partida = row['Partida'].day_name()
                dia_partida_pt = weekday_ptbr.get(dia_semana_partida, '')
                st.write(f"- **Partida:** {dia_partida_pt}, {row['Partida'].strftime('%d/%m/%Y')}")
            else:
                st.write("Partida: -")
                
            st.write(f"- **Tipo do Preço:** {row['Tipo do Preço']}")
            st.markdown(f"- **Link:** [Booking]({row['Link do Booking']})")

            # Botão de seleção: desabilitado se já selecionado
            st.button(
                f"Selecionar este Hotel",
                key=f"select_hotel_btn_{hotel_name}_{index}", # Chave única para cada botão
                on_click=select_hotel, # Chama a função ao clicar
                args=(hotel_name,), # Argumento para a função
                disabled=is_selected # Desabilita se for o selecionado
            )

# Garante que o preço do hotel selecionado seja usado no cálculo final
if st.session_state.selected_hotel_name:
    selected_hotel_data = df_hoteis_original[df_hoteis_original['Nome do Hotel'] == st.session_state.selected_hotel_name]
    if not selected_hotel_data.empty:
        current_hotel_price = selected_hotel_data['Preço por Período (R$)'].iloc[0]
        st.success(f"✔️ **Hotel Selecionado:** {st.session_state.selected_hotel_name} ({formatar_moeda(current_hotel_price)})")
    else:
        # Caso o hotel selecionado não seja mais encontrado (e.g., dados mudaram)
        current_hotel_price = 0.0
        st.warning("Hotel selecionado anteriormente não encontrado nos dados atuais. Por favor, faça uma nova seleção.")
        st.session_state.selected_hotel_name = None # Resetar seleção

st.markdown("---")

# --- 2. Seleção de Passagens Aéreas ---
st.subheader("✈️ 2. Escolha as Passagens Aéreas")

st.write("Selecione uma passagem de **IDA** e uma de **VOLTA**:")

col_ida, col_volta = st.columns(2)

# Passagens de IDA
with col_ida:
    st.markdown("#### Passagens de IDA")
    passagens_ida = df_passagens_original[df_passagens_original['Sentido + Companhia + Origem + Destino'].str.contains('Ida')]
    
    for index, row in passagens_ida.iterrows():
        passagem_info = row['Sentido + Companhia + Origem + Destino']
        is_selected = (st.session_state.selected_passagem_ida == passagem_info)
        
        with st.container(border=True):
            # Extrai Companhia e Rota para exibição mais limpa
            match_info = re.match(r'Ida \| (.*?) \| (.*)', passagem_info)
            if match_info:
                companhia = match_info.group(1).strip()
                rota = match_info.group(2).strip()
                st.markdown(f"**{companhia}**")
                st.write(f"- Rota: {rota}")
            else:
                st.markdown(f"**{passagem_info}**") # Fallback se o regex falhar
            
            st.write(f"- Preço Voo: {formatar_moeda(row['Preço (R$)'])}")
            st.write(f"- Preço Bagagem: {formatar_moeda(row['Preço da Bagagem (R$)'])}")
            st.write(f"- **Total:** {formatar_moeda(row['Total (R$)'])}")
            
            st.button(
                f"Selecionar Ida",
                key=f"select_ida_btn_{passagem_info}",
                on_click=select_passagem_ida,
                args=(passagem_info,),
                disabled=is_selected
            )

# Passagens de VOLTA
with col_volta:
    st.markdown("#### Passagens de VOLTA")
    passagens_volta = df_passagens_original[df_passagens_original['Sentido + Companhia + Origem + Destino'].str.contains('Volta')]
    
    for index, row in passagens_volta.iterrows():
        passagem_info = row['Sentido + Companhia + Origem + Destino']
        is_selected = (st.session_state.selected_passagem_volta == passagem_info)
        
        with st.container(border=True):
            # Extrai Companhia e Rota para exibição mais limpa
            match_info = re.match(r'Volta \| (.*?) \| (.*)', passagem_info)
            if match_info:
                companhia = match_info.group(1).strip()
                rota = match_info.group(2).strip()
                st.markdown(f"**{companhia}**")
                st.write(f"- Rota: {rota}")
            else:
                st.markdown(f"**{passagem_info}**") # Fallback se o regex falhar
            
            st.write(f"- Preço Voo: {formatar_moeda(row['Preço (R$)'])}")
            st.write(f"- Preço Bagagem: {formatar_moeda(row['Preço da Bagagem (R$)'])}")
            st.write(f"- **Total:** {formatar_moeda(row['Total (R$)'])}")
            
            st.button(
                f"Selecionar Volta",
                key=f"select_volta_btn_{passagem_info}",
                on_click=select_passagem_volta,
                args=(passagem_info,),
                disabled=is_selected
            )

# Calculate selected flight prices
if st.session_state.selected_passagem_ida:
    selected_ida_data = df_passagens_original[
        df_passagens_original['Sentido + Companhia + Origem + Destino'] == st.session_state.selected_passagem_ida
    ]
    if not selected_ida_data.empty:
        current_passagem_ida_price = selected_ida_data['Total (R$)'].iloc[0]
        st.success(f"✔️ **Passagem de IDA Selecionada:** {st.session_state.selected_passagem_ida.split('|')[1].strip()} ({formatar_moeda(current_passagem_ida_price)})")
    else:
        current_passagem_ida_price = 0.0
        st.warning("Passagem de IDA selecionada anteriormente não encontrada. Por favor, faça uma nova seleção.")
        st.session_state.selected_passagem_ida = None

if st.session_state.selected_passagem_volta:
    selected_volta_data = df_passagens_original[
        df_passagens_original['Sentido + Companhia + Origem + Destino'] == st.session_state.selected_passagem_volta
    ]
    if not selected_volta_data.empty:
        current_passagem_volta_price = selected_volta_data['Total (R$)'].iloc[0]
        st.success(f"✔️ **Passagem de VOLTA Selecionada:** {st.session_state.selected_passagem_volta.split('|')[1].strip()} ({formatar_moeda(current_passagem_volta_price)})")
    else:
        current_passagem_volta_price = 0.0
        st.warning("Passagem de VOLTA selecionada anteriormente não encontrada. Por favor, faça uma nova seleção.")
        st.session_state.selected_passagem_volta = None

total_passagens_calculado = current_passagem_ida_price + current_passagem_volta_price
if total_passagens_calculado > 0:
    st.info(f"**Total de Passagens Aéreas Selecionadas:** {formatar_moeda(total_passagens_calculado)}")
else:
    st.info("Por favor, selecione uma passagem de IDA e uma de VOLTA para calcular o custo total das passagens.")


st.markdown("---")


# --- 3. Custos de Atrações (Fixos e Editáveis) ---
st.subheader("💸 3. Ajuste as Quantidades das Atrações") # Renumbered to 3

total_atracoes_calculado = 0.0

# Cria as colunas para cada linha de atração
for index, row in df_atracoes_original.iterrows():
    col1, col2, col3, col4 = st.columns([0.4, 0.2, 0.2, 0.2])

    with col1:
        st.write(f"**{row['Atrações']}**")
    with col2:
        st.write(f"{formatar_moeda(row['Valor (R$)'])}")
    with col3:
        # st.number_input para ajustar a quantidade
        quantity = st.number_input(
            f"Qtd {row['Atrações']}",
            min_value=0,
            value=int(row['Quantidade']),
            step=1,
            key=f"qty_{index}",
            label_visibility="collapsed" # Esconde o label acima do input
        )
    with col4:
        subtotal = row['Valor (R$)'] * quantity
        st.write(f"{formatar_moeda(subtotal)}")
        total_atracoes_calculado += subtotal

st.info(f"**Total de Custos de Atrações Fixos:** **{formatar_moeda(total_atracoes_calculado)}**")

st.markdown("---")

# --- 4. Seleção de Aluguel de Carro (em blocos com botão de seleção) ---
st.subheader("🚗 4. Escolha o Aluguel de Carro") # Renumbered to 4
st.write("Selecione um aluguel de carro da lista abaixo:")

# Criar colunas para os blocos de aluguel de carro
carro_blocks_container = st.container() # Cria um container para as colunas de carros
with carro_blocks_container:
    carro_cols = st.columns(cols_per_row) # Reutilizando o número de colunas

# Itera sobre cada carro para criar um bloco de seleção dentro de uma coluna
for index, row in df_aluguel_carro_original.iterrows():
    carro_type = row['Tipo do Carro']
    locadora = row['Locadora']
    is_selected = (st.session_state.selected_carro_type_locadora == (carro_type, locadora))

    # Usa o índice para determinar em qual coluna o bloco será colocado
    with carro_cols[index % cols_per_row]:
        # st.container para cada bloco de carro
        with st.container(border=True):
            st.markdown(f"**{row['Tipo do Carro']}** ({row['Locadora']})")
            st.write(f"- **Preço p/ Período:** {formatar_moeda(row['Preço por Período (R$)'])}")
            st.write(f"- **Preço p/ Dia:** {formatar_moeda(row['Preço por Dia (R$)'])}")
            st.write(f"- **Dias:** {row['Dias']}")
            st.write(f"- **Passageiros:** {row['Passageiros']}")
            st.write(f"- **Preço p/ Passageiro:** {formatar_moeda(row['Preço por Passageiro (R$)'])}")

            # Botão de seleção
            st.button(
                f"Selecionar este Carro",
                key=f"select_carro_btn_{carro_type}_{locadora}", # Chave única
                on_click=select_carro, # Chama a função ao clicar
                args=(carro_type, locadora), # Argumentos para a função
                disabled=is_selected # Desabilita se for o selecionado
            )

# Garante que o preço do carro selecionado seja usado no cálculo final
if st.session_state.selected_carro_type_locadora:
    selected_carro_data = df_aluguel_carro_original[
        (df_aluguel_carro_original['Tipo do Carro'] == st.session_state.selected_carro_type_locadora[0]) &
        (df_aluguel_carro_original['Locadora'] == st.session_state.selected_carro_type_locadora[1])
    ]
    if not selected_carro_data.empty:
        current_carro_price = selected_carro_data['Preço por Período (R$)'].iloc[0]
        st.success(f"✔️ **Aluguel de Carro Selecionado:** {st.session_state.selected_carro_type_locadora[0]} ({st.session_state.selected_carro_type_locadora[1]}) ({formatar_moeda(current_carro_price)})")
    else:
        # Caso o carro selecionado não seja mais encontrado
        current_carro_price = 0.0
        st.warning("Aluguel de carro selecionado anteriormente não encontrado nos dados atuais. Por favor, faça uma nova seleção.")
        st.session_state.selected_carro_type_locadora = None # Resetar seleção

st.markdown("---")

# --- Cálculo e Exibição do Custo Total da Viagem ---
# Aqui o cálculo é feito *antes* de exibir na sidebar e na tela principal
final_total_cost = current_hotel_price + total_passagens_calculado + total_atracoes_calculado + current_carro_price

# Exibe o custo total na sidebar
st.sidebar.markdown("---") # Separador visual na sidebar
st.sidebar.markdown("### 💰 Custo Total Estimado da Viagem") # Texto atualizado aqui
st.sidebar.markdown(f"**{formatar_moeda(final_total_cost)}**")


# Exibe o custo total na tela principal
st.header("💰 Custo Total Estimado da Viagem")
st.success(f"**O Custo Total Estimado da Sua Viagem é: {formatar_moeda(final_total_cost)}**")


# --- Estilos CSS personalizados ---
st.markdown("""
<style>
    p {
        font-size: 1.05em;
    }
    .st-emotion-cache-nahz7x { /* Target st.info and st.success message boxes */
        background-color: #e6f7ff;
        border-left: 5px solid #007bff;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        color: #000000;
    }
    .st-emotion-cache-nahz7x.stAlert-success {
        background-color: #e6ffe6;
        border-left: 5px solid #66cc66;
        color: #338833;
    }
    .st-emotion-cache-nahz7x p {
        font-size: 1.05em;
        font-weight: normal;
    }
    .st-emotion-cache-nahz7x.stAlert-success p {
        font-size: 1.3em;
        font-weight: bold;
    }
    .dataframe {
        font-size: 0.9em;
    }
    /* Ajustes para os botões de seleção e containers (os "blocos") */
    div[data-testid="stContainer"] {
        padding: 1rem;
        margin-bottom: 0.75rem;
        border: 1px solid #ccc; /* Borda padrão para o container */
        border-radius: 0.5rem;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1); /* Sombra suave para destacar o bloco */
        height: 100%; /* Garante que os containers tenham a mesma altura em uma linha */
        display: flex;
        flex-direction: column;
        justify-content: space-between; /* Empurra o botão para baixo */
    }
    div[data-testid="stContainer"] button { /* Estilo para o botão DENTRO do container */
        width: 100%; /* Botão ocupa toda a largura do bloco */
        margin-top: auto; /* Empurra o botão para a parte inferior do container */
    }
    /* Estilo geral para todos os botões (incluindo os de seleção) */
    .stButton > button {
        background-color: #007bff; /* Azul primário */
        color: white;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-size: 1.1em;
        border: none;
        cursor: pointer;
        transition: background-color 0.2s; /* Transição suave na cor */
    }
    .stButton > button:hover:enabled {
        background-color: #0056b3; /* Azul mais escuro ao passar o mouse */
        color: white !important;
    }
    .stButton > button:disabled { /* Estilo para o botão DESABILITADO (quando já selecionado) */
        background-color: #cccccc; /* Cinza */
        color: #666666; /* Texto cinza */
        cursor: not-allowed;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #FF4B4B; /* Cor vermelha para títulos */
    }
    a { /* Estilo para links em geral */
        color: #007bff;
        text-decoration: none;
    }
    a:hover {
        text-decoration: underline;
    }
    /* Ajusta o espaçamento entre as colunas - Este seletor pode variar entre versões do Streamlit */
    /* Você pode precisar inspecionar o elemento para encontrar o correto para sua versão */
    div[data-testid="column"] { /* Seletor comum para as colunas */
        gap: 1rem; /* Espaço entre as colunas */
    }
    div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] {
        gap: 1rem; /* Outro possível seletor para ajustar o gap entre colunas */
    }
</style>
""", unsafe_allow_html=True)