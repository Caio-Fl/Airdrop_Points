# Importar Bibliotecas Python
import requests
import json

# Inicialização
base_url = "https://www.data-openblocklabs.com/sonic/all-users-points-stats" # endereço base de request dos dados
items_per_page = 10000 # número de endereços lidos por request
total_sonic_accured = 0 # inicialização de pontos totais
total_eco_accured  = 0
total_passive_accured = 0
total_active_accured = 0
page = 1 # contador para  inicial
count = 0
# Loop de leitura
while True:
    print(f"Lendo Sonic Página {page}...")
    url = f"{base_url}?size={items_per_page}&page={page}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        leaderboard = data.get("items", [])
        
        if not leaderboard:
            break
        print(len(leaderboard))
        for entry in leaderboard:
            sonic_accured = float(entry.get("sonic_points", 0))
            eco_accured = float(entry.get("ecosystem_points", 0))
            passive_accured = float(entry.get("passive_liquidity_points", 0))
            active_accured = float(entry.get("active_liquidity_points", 0))
            total_sonic_accured += round(sonic_accured,2)  
            total_eco_accured += round(eco_accured,2)
            total_passive_accured += round(passive_accured,2)  
            total_active_accured += round(active_accured,2)   
            count += 1
            if count == 100:
                top100 = total_sonic_accured 
        page += 1
        print(total_sonic_accured, total_eco_accured, total_passive_accured, total_active_accured)
        if page == 70:
            break
    else:
        print(f"Erro ao coletar dados na página {page}. Status Code:", response.status_code)
        break
top100p = top100/total_sonic_accured
print("TOTAL DE SONIC PONTOS = ",total_sonic_accured, "XP")
print("TOTAL DE PONTOS DE LIQUIDEZ ATIVA = ",total_passive_accured, "XP")
print("TOTAL DE PONTOS DE LIQUIDEZ PASSIVA = ",total_active_accured, "XP")
print(total_sonic_accured, total_eco_accured, total_passive_accured, total_active_accured,top100p,count)