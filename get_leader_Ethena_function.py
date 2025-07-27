def get_ethena_Data():
    import requests

    url = "https://app.ethena.fi/api/leaderboard"

    # Definindo os cabeçalhos da requisição
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://app.ethena.fi/leaderboard",
        "Accept": "*/*"
    }

    try:
        # Requisição GET com cabeçalhos
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()

            # Total global de pontos e total de wallets
            total_points = data["aggregateWallet"]["accumulatedTotalShardsEarnedSum"]
            total_wallets = data["aggregateWallet"]["count"]

            # Lista das wallets (top 100 por padrão no retorno)
            top_wallets = data.get("queryWallet", [])

            # Soma dos pontos das top 100 wallets
            top100_sum = sum(wallet["accumulatedTotalShardsEarned"] for wallet in top_wallets[:100])

            # Calcula o percentual das top 100
            top100 = (top100_sum / total_points)

            return total_points, total_wallets, top100

        else:
            print(f"Erro ao acessar API Ethena. Status code: {response.status_code}")
            return None, None, None

    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        return None, None, None
