def get_ethena_Data():
    import requests

    # URL da API
    url = "https://app.ethena.fi/api/leaderboard"

    # Requisição GET
    response = requests.get(url)

    # Verifica se foi bem-sucedido
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
