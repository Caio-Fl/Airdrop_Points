def get_leader_kyros_function():
    # Importar Bibliotecas Python
    import requests
    import json
    import re

    # Inicialização
    url = "https://points-api.kyros.fi/leaderboard" # endereço base de request dos dados

    response = requests.get(url)
   
    total_accured = 0 
    count = 0
    if response.status_code == 200:
        data = response.json()
        leaderboard = data.get("leaderboard", [])
        for entry in leaderboard:
            accured = entry.get("totalPoints", "0")
            total_accured += int(accured)
            count += 1
            if count == 100:
                top100 = total_accured
    else:
        print(f"Erro ao coletar dados. Status Code:", response.status_code)

    top100p = top100/total_accured
    total_users = count

    url = "https://api.coingecko.com/api/v3/simple/price?ids=kyros-restaked-sol&vs_currencies=usd"
    response2 = requests.get(url)
    data2 = response2.json()
    price = data2.get("kyros-restaked-sol", {}).get("usd")
    KyAsUSD = price
    

    url = "https://www.exponent.finance/farm/kysol-30Sep25"
    headers = {
        "User-Agent": "Mozilla/5.0"  # importante para evitar bloqueios básicos
    }

    response3 = requests.get(url, headers=headers)
    
    if response3.status_code == 200:
        html = response3.text
    else:
        print(f"Erro: {response3.status_code}")

    palavra_chave = "2r8NaP6G69vb1AgkWWLGQ8SVZLAcwXgWuq19a3zWo9gN"

    # Captura tudo após a palavra-chave
    resultado = html.split(palavra_chave, 1)[-1]
    texto = resultado[:800]
    texto_limpo = texto.encode().decode('unicode_escape')
    match = re.search(r'"underlyingYieldsPct":([\d.]+)', texto_limpo)
    if match:
        Ky_unApy = float(match.group(1))
    else:
        Ky_unApy = 0.07
    return(total_accured,Ky_unApy,KyAsUSD,total_users,top100p)