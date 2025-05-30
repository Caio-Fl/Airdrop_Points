from dune_client.client import DuneClient
import pandas as pd

# Conexão com a API da Dune
dune = DuneClient("MzEYG7lt2WPpEJoYM385RO1ijDvVW4hb")
query_result = dune.get_latest_result(4993467)
data = query_result.result.rows

# Criando DataFrame
df = pd.DataFrame(data)

# Dicionários de multiplicadores
multipliers = {
    'Classic': {
        'NO Commitment': 1,
        'Init. 3 month': 3,
        'Init. 6 month': 5
    },
    'Maxi': {
        'NO Commitment': 5,
        'Init. 3 month': 10.5,
        'Init. 6 month': 17.5
    }
}

# Cálculo dos multiplicadores e XP
def get_multiplier(row):
    return multipliers[row['Mode']][row['Commit']]

df['Multiplier'] = df.apply(get_multiplier, axis=1)
df['XP'] = df['Shares'] * df['Multiplier'] * 0.03

# Ordenando Mode: Classic primeiro
df['Mode'] = pd.Categorical(df['Mode'], categories=['Classic', 'Maxi'], ordered=True)
df['Commit'] = pd.Categorical(df['Commit'], categories=['NO Commitment', 'Init. 3 month', 'Init. 6 month'], ordered=True)
df = df.sort_values(by=['Mode', 'Commit'])

# Reorganizando colunas
df = df[['Mode', 'Commit', 'Shares', 'Multiplier', 'XP']]

# Configurando exibição sem notação científica
pd.set_option('display.float_format', '{:.1f}'.format)

# Exibindo DataFrame e total de XP
print(df)

total_xp = df['XP'].sum()
print(f"Total XP: {total_xp:,.2f}")

import requests
import json

url = "https://mainnet.permissionless-points.huma.finance/graphql"

payload = {
    "query": """
    query Query {
      myRankingEntry {
        ... on LeaderboardItem {
          accountId
          accountName
          points
          referredCount
          ranking
        }
        ... on PermissionlessGraphqlError {
          errMessage
        }
      }
    }
    """
}

headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://app.huma.finance/",
    "Origin": "https://app.huma.finance",
    "Cookie": (
        "__hstc=44435643.b8d9a08f9a32d9566375c60b28efb5c8.1738259368379.1738259368379.1738259368379.1; "
        "hubspotutk=b8d9a08f9a32d9566375c60b28efb5c8; "
        "session_id:900=\"\\\"9597ae08-2688-4ee6-9303-c04315befb54\\\".6y5cbDfZ8h-AIxgF67hvv7hR--o\"; "
        "id_token:9xhCFJVtaSLmR9dEaPQEZDvqzeGXhNonVKLWxhpj9RCL:900=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
        "VP_j5K_dhx5zycwcb5NsItQhgN4RDZsj-BCkJjCSkI_V_icHYAZZpwx-f-6MBVHeIWlZ7iy-O4kcW_FADR8sojKpd8gecUGjak4VIu5eEWqCZ8zIaGZ52E5zW2vvdsKpuUfo6B5zcnxQk3Ed2Z3TOOHmOiSl0AM8rGMvuLVHHTgTnWRbbgdNGpm1CaGbe5Se4ZU-fz9ApU4fR0ExQ3Ua5G8kn-0d_2c6Sc832orlpgoUfY4umMvEeMPemI9VctMvgiBKUwe5HxhtK5wReHWPE1203O2g54h781KQdkvu7K3aAMnWxeeldHyshFlvV68_RGqK-plGYlqogdXokGLJ6w; "
        "account_token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzYTBiODYzYy0xYjgyLTQ0MGYtODJjZC1kYmEwZjRiMGIxNTMiLCJleHAiOjE3NDg1NTYyMzIsImlhdCI6MTc0ODI5NzAzMiwiaXNzIjoiaHVtYS5maW5hbmNlIn0.EkGtNLT_h6rPl69IQFcTc_yJH2l9c79x_swIIpKQKddO-dc9-uCRim7m1qkDbQWalUt4L34ZaDJoA0HbeIfiaoU2JsCdMgTDhZi5XgxPmHw4I_PMakopRH2HssT9K98cOcLlom9txpMLQY0ANLXXAqqbiqI0E3YyCWTdVIYsnWM4Yvo6oeFZojVHjgw3MpS7AvibXJcwKgtJYqMXTh5YbwJfhUwx0GKUfAVJf3Uk768tQoOGghISkGVtr3aMFWk1JYPtESAnuZmXN_gBsyiJMPPw7JRF0IxB3QHJEkUdvaDBAueDFXu6rlbgNQitWrmCidUUszK9Q8bASWAtYnKIhA"
    )
}


headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://app.huma.finance/",
    "Origin": "https://app.huma.finance",
    "Cookie": (
        "__hstc=44435643.b8d9a08f9a32d9566375c60b28efb5c8.1738259368379.1738259368379.1738259368379.1; "
        "hubspotutk=b8d9a08f9a32d9566375c60b28efb5c8; "
        "session_id:900=\"\\\"9597ae08-2688-4ee6-9303-c04315befb54\\\".6y5cbDfZ8h-AIxgF67hvv7hR--o\"; "
        "id_token:43782950-44ab-4fdc-8b46-e09df32e7fc5:900=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
        "VP_j5K_dhx5zycwcb5NsItQhgN4RDZsj-BCkJjCSkI_V_icHYAZZpwx-f-6MBVHeIWlZ7iy-O4kcW_FADR8sojKpd8gecUGjak4VIu5eEWqCZ8zIaGZ52E5zW2vvdsKpuUfo6B5zcnxQk3Ed2Z3TOOHmOiSl0AM8rGMvuLVHHTgTnWRbbgdNGpm1CaGbe5Se4ZU-fz9ApU4fR0ExQ3Ua5G8kn-0d_2c6Sc832orlpgoUfY4umMvEeMPemI9VctMvgiBKUwe5HxhtK5wReHWPE1203O2g54h781KQdkvu7K3aAMnWxeeldHyshFlvV68_RGqK-plGYlqogdXokGLJ6w; "
        "account_token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzYTBiODYzYy0xYjgyLTQ0MGYtODJjZC1kYmEwZjRiMGIxNTMiLCJleHAiOjE3NDg1NTYyMzIsImlhdCI6MTc0ODI5NzAzMiwiaXNzIjoiaHVtYS5maW5hbmNlIn0.EkGtNLT_h6rPl69IQFcTc_yJH2l9c79x_swIIpKQKddO-dc9-uCRim7m1qkDbQWalUt4L34ZaDJoA0HbeIfiaoU2JsCdMgTDhZi5XgxPmHw4I_PMakopRH2HssT9K98cOcLlom9txpMLQY0ANLXXAqqbiqI0E3YyCWTdVIYsnWM4Yvo6oeFZojVHjgw3MpS7AvibXJcwKgtJYqMXTh5YbwJfhUwx0GKUfAVJf3Uk768tQoOGghISkGVtr3aMFWk1JYPtESAnuZmXN_gBsyiJMPPw7JRF0IxB3QHJEkUdvaDBAueDFXu6rlbgNQitWrmCidUUszK9Q8bASWAtYnKIhA"
    )
}


response = requests.post(url, headers=headers, data=json.dumps(payload))

if response.status_code == 200:
    data = response.json()
    print(json.dumps(data, indent=2))
else:
    print(f"Erro {response.status_code}")
    print(response.text)
