import requests
import json
import time
from datetime import datetime, timezone, timedelta

headers = {
        "path": "/v1/graphql",
        "Content-Type": "application/json",
        "Accept": "*/*"
}

payload = {"operationName":"restakingFund","variables":{},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"d3874b3fa022f6a3d4b28c26525d6a49dbaf3424c8e94635e04db8bb4866de7f"}}}
url = f"https://api.fragmetric.xyz/v1/graphql"
response = requests.post(url, json=payload, headers=headers)
data = response.json()
jsonn = json.loads(response.text)
print(jsonn)
solAsUSD = float(data.get("data", {}).get("solAsUSD", "0"))
fragAPYarray = data.get("data", {}).get("restakingFunds", [{}])
fragAPY = float(fragAPYarray[0].get("receiptToken", {}).get("metadata", {}).get("apy", {}))
fragAsUSD = float(fragAPYarray[0].get("receiptToken", {}).get("metadata", {}).get("oneTokenAsUSD", {}))
fragBySol = fragAsUSD/solAsUSD


payload = {"operationName":"fPointEstimations","variables":{},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"423082c3bd12d59281c0463274f998270efa80af1316ed7647a51ee85be536f1"}}}
url = f"https://api.fragmetric.xyz/v1/graphql"
response = requests.post(url, json=payload, headers=headers)
data2 = response.json()
total = data2.get("data", {}).get("fPointEstimations", {}).get("totalAccrualAmount", "0")
total_users = data2.get("data", {}).get("fPointEstimations", {}).get("usersCount", "0")
total_accured = round(float(total)/10000,0)
print(total_accured,fragAPY,solAsUSD,fragAsUSD,fragBySol,total_users)

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

url = "https://xpon-json-api-staging-650968662509.europe-west3.run.app/api/tokens"
response2 = requests.get(url)
data2 = response2.json()
value = data2.get("data", [])
KyAsUSD = value[15].get("priceUsd", 0)

url = "https://www.exponent.finance/farm/kysol-14Jun25"
headers = {
    "User-Agent": "Mozilla/5.0"  # importante para evitar bloqueios básicos
}

response3 = requests.get(url, headers=headers)

if response3.status_code == 200:
    html = response3.text
else:
    print(f"Erro: {response3.status_code}")

palavra_chave = "kySo1nETpsZE2NWe5vj2C64mPSciH1SppmHb4XieQ7B"

# Captura tudo após a palavra-chave
resultado = html.split(palavra_chave, 1)[-1]
texto = resultado[:800]
texto_limpo = texto.encode().decode('unicode_escape')

match = re.search(r'"underlyingYieldsPct":([\d.]+)', texto_limpo)
if match:
    Ky_unApy = float(match.group(1))
else:
    Ky_unApy = 0.07

print(total_accured,Ky_unApy,KyAsUSD,total_users,top100p)