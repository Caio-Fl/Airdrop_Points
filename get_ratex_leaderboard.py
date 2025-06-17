import requests
from decimal import Decimal

url = "https://api.rate-x.io/"

headers = {
    "Content-Type": "application/json",
    "Origin": "https://app.rate-x.io",
    "Referer": "https://app.rate-x.io/",
    "Sessionid": "6h63/Jx6qLkslWrOSc9D3A=="
}

payload = {
    "serverName": "AdminSvr",
    "method": "queryRatexPointsRanking",
    "content": {
        "cid": "4c6dba8b-822b-4f3e-ef5f-7b9ac8ded60d",
        "ranking": 1000
    }
}

Wallets = 0

response = requests.post(url, headers=headers, json=payload)

if response.status_code == 200:
    data = response.json()
    
    try:
        ranking_list = data["data"]
    except (KeyError, TypeError):
        print("Erro ao acessar dados da resposta:")
        exit()

    # Inicializa acumuladores
    total_points_sum = Decimal(0)
    lp_points_sum = Decimal(0)
    earn_points_sum = Decimal(0)
    trade_points_sum = Decimal(0)

    for user in ranking_list:
        total_points_sum += Decimal(user.get("total_points", "0") or "0")
        lp_points_sum += Decimal(user.get("lp_points", "0") or "0")
        earn_points_sum += Decimal(user.get("earn_points", "0") or "0")
        trade_points_sum += Decimal(user.get("trade_points", "0") or "0")
        Wallets += 1

    print("Pontos acumulados:")
    print(f"Total Points: {total_points_sum:,.2f}")
    print(f"LP Points: {lp_points_sum:,.2f}")
    print(f"Earn Points: {earn_points_sum:,.2f}")
    print(f"Trade Points: {trade_points_sum:,.2f}")
    print(f"Wallets: {Wallets:,.2f}")

else:
    print(f"Erro {response.status_code}: {response.text}")
