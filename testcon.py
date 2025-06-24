import requests
import json
Request_URL = "https://discord.com/api/v9/channels/1314347387942211605/messages?limit=5"
code = "MTIyMTI1MjYwNzQxNTE1Njc3MA.Gg8_XS"
code2=".BGfC4ic2rEyvs0bPk_jh3DSxRTNTlfbYZOjY34"
    
headers = {
    "Authorization" : code+code2
}

res = requests.get(Request_URL, headers=headers)
jsonn = json.loads(res.text)
print(jsonn)