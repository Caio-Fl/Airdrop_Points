def get_leader_Gaib_function():    
    import requests

    # Endpoint do leaderboard com endereço de exemplo
    url = "https://pre-vault-api.gaib.ai/points/leaderboard?page=1&pageSize=100"

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Origin": "https://aid.gaib.ai",
        "Referer": "https://aid.gaib.ai/",
    }

    response = requests.get(url, headers=headers, verify=False)
    data = response.json()


    # Dados principais
    tvl = round(data['data']['global_stats']['total_network_raw_deposits_usd']/1000000,3)
    leaderboard = data['data']['leaderboard']
    total_users = data['data']['pagination']['total_items']
    estimated_total_points = data['data']['global_stats']['estimated_total_network_points']

    # Soma dos pontos dos 100 primeiros usuários
    top_100_total_points = sum(user['total_points_earned_estimate'] for user in leaderboard)

    # Porcentagem dos pontos dos top 100 em relação ao total estimado
    top100p = (top_100_total_points / estimated_total_points)
    print(tvl)

    return(estimated_total_points,top100p,total_users,tvl)
