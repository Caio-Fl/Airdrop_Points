import requests
import streamlit as st

def get_data_from_google_sheets():
    # URL da API do Google Sheets para acessar a planilha pública
    sheet_id = '1JODKmjCVKkyL2ziuIHa03TxEHeQdb6w4t8DR8J7qdhQ'
    range_ = 'Ethena!C3:C3'  # Defina o intervalo que você deseja acessar
    api_key = 'AIzaSyC4C4bMviJpBIuR7XXCqqPF81JrrYitlro'
    url = f'https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/{range_}?key={api_key}'

    # Substitua YOUR_API_KEY pela sua chave de API do Google
    response = requests.get(url)
    print(response)
    
    if response.status_code == 200:
        data = response.json()
        st.write(data)  # Exibe os dados no Streamlit
        return data
    else:
        st.error(f"Erro na requisição: {response.status_code}")
        return None

# Chama a função para puxar os dados
data = get_data_from_google_sheets()
