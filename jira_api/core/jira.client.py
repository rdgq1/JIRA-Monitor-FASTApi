import requests
from requests.auth import HTTPBasicAuth
import os

JIRA_URL = os.environ.get("JIRA_URL") # Alterado para variável de ambiente
EMAIL = os.environ.get("JIRA_EMAIL") # Alterado para variável de ambiente
API_TOKEN = os.environ.get("JIRA_API_TOKEN") # Alterado para variável de ambiente
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def buscar_chamados(jql: str, expand: str = None):
    url = f"{JIRA_URL}/rest/api/3/search"
    params = {
        "jql": jql,
        "maxResults": 200,
        "fields": "summary,status,updated,resolutiondate,assignee,reporter", 
    }
    if expand:
        params["expand"] = expand

    response = requests.get(
        url,
        headers=HEADERS,
        params=params,
        auth=HTTPBasicAuth(EMAIL, API_TOKEN)
    )
    if response.status_code == 200:
        return response.json().get("issues", [])
    else:
        raise Exception(f"Erro ao buscar chamados no Jira: {response.status_code} - {response.text}")
