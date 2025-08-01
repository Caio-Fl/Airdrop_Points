import requests
import time

url = "https://app.hyperbeat.org/api/points"

query = """
query GetLeaderboardList($page_size: Int!, $page_number: Int!) {
  cron_get_ranked_etherfi_points_new(args: {
    provider_filter: "hyperbeat",
    page_size: $page_size,
    page_number: $page_number
  }) {
    rank
    address
    total_value
  }
}
"""

headers = {
    "Content-Type": "application/json",
    "Origin": "https://app.hyperbeat.org",
    "Referer": "https://app.hyperbeat.org/hyperfolio",
}

page_size = 1000
page_number = 1

all_users = []

while True:
    print(f"Buscando página {page_number}...")
    payload = {
        "query": query,
        "variables": {
            "page_size": page_size,
            "page_number": page_number
        }
    }
    
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    
    users = data["data"]["cron_get_ranked_etherfi_points_new"]
    
    if not users:
        break
    
    all_users.extend(users)
    
    page_number += 1
    time.sleep(0.1)  # para evitar bloqueio

print(f"\nTotal de usuários encontrados: {len(all_users)}")

# Total de pontos de todo mundo
total_pontos = sum(user["total_value"] for user in all_users)
print(f"Total geral de pontos: {total_pontos:,}")

# Top 100
top100 = sorted(all_users, key=lambda x: x["rank"])[:100]
total_pontos_top100 = sum(user["total_value"] for user in top100)
print(f"Total de pontos no top 100: {total_pontos_top100:,}")
