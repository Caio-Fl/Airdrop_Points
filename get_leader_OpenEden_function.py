def get_leader_OpenEden_function(): 

    # Importar Bibliotecas Python
    import requests
    import json

    # Inicialização
    base_url = "https://prod-gw.openeden.com/ps/user/leaderboard" # endereço base de request dos dados
    auth_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ3YWxsZXRBZGRyZXNzIjoiMHg3NWQ4NWNhNDk3MTYyNWI4ZjE3OWUzZDM5Y2Q0YWE3MmJlMmM2ZDRiIiwiYXV0aFRva2VuVmVyc2lvbiI6MCwiaWF0IjoxNzQ0NTgzNTk1LCJleHAiOjE3NDQ4NDI3OTV9.LdDBODcI9Mm7HvbApgcy1-rxZuoG_WL65WVUG-8UBCg"
    headers = {"Authorization": f"Bearer {auth_token}",
            }
    url = f"{base_url}"

    headers = {
        "path": "/ps/user/leaderboard",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {auth_token}",
    }

    total_accured = 0 # inicialização de pontos totais
    page = 1 # contador para  inicial
    count = 0
    while True:
        print(f"Lendo OpenEden Página {page}...")

        payload = {"pageNumber":page,"limit":1000}
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 201:
            data = response.json()
            leaderboard = data.get("leaderboardData", [])

            if not leaderboard:
                break
            for entry in leaderboard:
                accured = entry.get("totalPoints", "0")
                total_accured += int(accured) 
                count += 1
                if count == 100:
                    top100 = total_accured
            page += 1
        else:
            print(f"Erro ao coletar dados na página {page}. Status Code:", response.status_code)
            break
    top100p = top100/total_accured
    print("TOTAL PONTOS =", total_accured, " XP")
    return(total_accured,top100p,count)