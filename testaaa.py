import cloudscraper

url = "https://app.titan.exchange/api/wallet-stats/stats"

payload = {
    "wallet_address": "9xhCFJVtaSLmR9dEaPQEZDvqzeGXhNonVKLWxhpj9RCL"
}

scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'mobile': False
    }
)

response = scraper.post(url, json=payload)

print("Status:", response.status_code)
print("Resposta:", response.text)
