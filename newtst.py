import requests

def get_all_total_points(asset="weETH", limit=100):
    url = "https://api.expedition.mitosis.org/v1/epoch/leaderboard"
    offset = 0
    total_sum = 0.0
    total_wallets = 0

    while True:
        params = {"asset": asset, "limit": limit, "offset": offset}
        res = requests.get(url, params=params)

        if res.status_code != 200:
            raise Exception(f"Erro na requisição: {res.status_code}")

        data = res.json()
        items = data.get("items", [])

        if not items:
            break  # terminou as páginas

        # somar pontos da página
        total_sum += sum(float(item["totalPoints"]) for item in items)
        total_wallets += len(items)

        # ir pra próxima página
        offset += limit

    return total_sum, total_wallets

if __name__ == "__main__":
    total, wallets = get_all_total_points("weETH")
    print(f"Soma total dos pontos: {total}")
    print(f"Total de wallets: {wallets}")
    print(f"Média de pontos por wallet: {total / wallets if wallets else 0}")
