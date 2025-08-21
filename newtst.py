import requests
import json

# Endereço da carteira
address = "0x2A78c88C4012544D11E41736505B8D67abBA0532"

# Endpoint da API da Lombard
url = f"https://mainnet.prod.lombard.finance/api/v1/referral-system/season-1/points/{address}"

# Requisição
response = requests.get(url)
response.raise_for_status()
data = response.json()

# Exibindo os dados principais
print(f"\n🔷 Total de Pontos: {data['total']:,.2f}")
print(f"🔹 Total sem Badges: {data['total_without_badges']:,.2f}")
print(f"🎖️ Badges: {data['badges']:,.0f}")
print(f"💼 Holding Points: {data['holding_points']:,.6f}")
print(f"📊 Protocol Points: {data['protocol_points']:,.2f}")

# Exibindo o breakdown dos pontos por protocolo
print("\n📋 Distribuição por Protocolo:")
for protocol, points in data.get("protocol_points_map", {}).items():
    print(f" - {protocol}: {points:,.2f}")
