
import requests
import json

def retrieve_messages(Request_URL,headers):
    res = requests.get(Request_URL, headers=headers)
    jsonn = json.loads(res.text)
    org_res = []
    org_author = []
    org_author_name = []
    org_mention = []

    for value in jsonn:
        #print(value['author']['username'],': ',value['content'], '\n')
        print(org_res)
        org_res.append(value['content'])
        org_author.append(value['author']['id'])
        org_author_name.append(value['author']['username'])
        if value['mentions']:
            org_mention.append(value['mentions'][0]['username'])
        else:
            org_mention.append(' ')

    return res, org_res, org_author, org_mention, org_author_name


code = "MTIyMTI1MjYwNzQxNTE1Njc3MA.G01IGX"
code2=".ueBpDmaelTgSaI0Oq6Q6ll4XvjeH5b6ycRUYTc"

headers = {
    "Authorization" : code+code2
}

Request_URL = "https://discord.com/api/v9/channels/1314347387942211605/messages?limit=5"
res, org_res, org_author, org_mention, org_author_name = retrieve_messages(Request_URL,headers)


print(org_res)