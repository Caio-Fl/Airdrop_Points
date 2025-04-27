def get_leader_Level_function():

    # Importar Bibliotecas Python
    import requests
    import json

    # Inicialização
    base_url = "https://api.level.money/v1/xp/balances/leaderboard" # endereço base de request dos dados
    items_per_page = 1000 # número de endereços lidos por request
    total_accured = 0 # inicialização de pontos totais
    page = 1 # contador para  inicial
    count = 0
    # Loop de leitura
    while True:
        print(f"Lendo Level Página {page}...")
        url = f"{base_url}?page={page}&take={items_per_page}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            leaderboard = data.get("leaderboard", [])

            if not leaderboard:
                break

            for entry in leaderboard:
                accured = entry.get("balance", {}).get("accrued", "0")
                total_accured += int(accured)  
                count += 1
                if count == 100:
                    top100 = total_accured  
            page += 1
        else:
            print(f"Erro ao coletar dados na página {page}. Status Code:", response.status_code)
            break
    top100p = top100/total_accured
    print("TOTAL DE PONTOS = ",total_accured, "XP")
    return(total_accured,top100p,count)