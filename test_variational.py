import requests

BASE_URL = "https://omni-client-api.prod.ap-northeast-1.variational.io"

def fetch_stats():
    resp = requests.get(f"{BASE_URL}/metadata/stats")
    resp.raise_for_status()
    return resp.json()

stats = fetch_stats()

# Platform metrics
print(f"24h Volume: ${float(stats['total_volume_24h']):,.2f}")
print(f"TVL: ${float(stats['tvl']):,.2f}")
print(f"Open Interest: ${float(stats['open_interest']):,.2f}")
print(f"Markets: {stats['num_markets']}")

# List all tokens
print("\nListings:")
for listing in stats["listings"]:
    try:
        # API retorna string → convertemos para float
        funding_rate = float(listing["funding_rate"])  # ex: 0.12 = 12% ao ano

        # Converte para % por hora
        hourly_pct = (funding_rate / (365 * 24)) * 100

        print(f"  {listing['ticker']}: {hourly_pct:.6f}%/h")

    except (ValueError, TypeError):
        print(f"  {listing['ticker']}: funding inválido")
