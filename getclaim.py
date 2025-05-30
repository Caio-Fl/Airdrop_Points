import requests
import time
import json
import streamlit as st

from mistralai import Mistral
from dotenv import load_dotenv
from mistralai.models import UserMessage
from mistralai.models import File
load_dotenv("apikey.env")  # Load .env file
import os
#from mistralai.client import MistralClient
os.environ["MISTRAL_API_KEY"] = "3DwmTII9fJMoAJRN8XoXf1Wg6aMKg7tu"


def mistral_AI(question,language,model,personality):

    #api_key = os.environ["3DwmTII9fJMoAJRN8XoXf1Wg6aMKg7tu"]
    import os
    from dotenv import load_dotenv
    max_retries = 5
    load_dotenv("apikey.env")  # Load .env file
    api_key = os.getenv("MISTRAL_API_KEY")

    if api_key is None:
        print("Error: API key is missing! Set MISTRAL_API_KEY. \n")
    else:
        print("API Key loaded successfully! \n")
    
    for attempt in range(max_retries):
        try:
            client = Mistral(api_key=api_key)
            if language == "ingles":
                inicial = " "

            chat_response = client.chat.complete(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": personality,
                    }, 
                    {
                        "role": "user", 
                        "content": question
                    }, 
                    #UserMessage(content= "I'm fine, i trust you're too?")
                ],
            )
            if chat_response.choices[0].message.content is not None:
                res = {"content" : chat_response.choices[0].message.content}
            else:
                res = {"content" : ''}
            return res
        except Exception as e:
            time.sleep(5)
    return {"content": "Erro ao tentar acessar a IA Mistral."}

def retrieve_messages(Request_URL,headers):
    res = requests.get(Request_URL, headers=headers)
    jsonn = json.loads(res.text)
    org_res = []
    org_author = []
    org_author_name = []
    org_mention = []

    for value in jsonn:
        #print(value['author']['username'],': ',value['content'], '\n')
        org_res.append(value['content'])
        org_author.append(value['author']['id'])
        org_author_name.append(value['author']['username'])
        if value['mentions']:
            org_mention.append(value['mentions'][0]['username'])
        else:
            org_mention.append(' ')

    return res, org_res, org_author, org_mention, org_author_name

def mirror_list(arr):
    return arr[::-1]

code = "MTIyMTI1MjYwNzQxNTE1Njc3MA.GRCiQ6"
code2=".JYJrhDkJOo07MpA-PsPrYb4azUHVu4D9n27U6A"
headers = {
    "Authorization" : code+code2
}
print(headers)
Request_URL = "https://discord.com/api/v9/channels/1314347387942211605/messages?limit=5"
res, org_res, org_author, org_mention, org_author_name = retrieve_messages(Request_URL,headers)
respostas = mirror_list(org_res)
print(respostas)
Resp_sem_tag = [item.replace("<@&1291085400336760864>", "") for item in respostas]

question = "\n\n".join(Resp_sem_tag)
personality = """Rewrite the present text in a topic structure in few lines. Do not show topic structure title."""

result = mistral_AI(question,"ingles","mistral-large-latest",personality)

# IA pode ser uma lista de dicionários com 'content'
st.markdown(
    """
    <style>
        a {
            color: orange !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)
if isinstance(result , dict) and 'content' in result:
    st.markdown(
    f"""
    <div style='font-size: 22px; line-height: 1.6;'>
        {"\n" + result['content']}
    </div>
    """,
    unsafe_allow_html=True
    )

print("** ** \n" + result['content'])