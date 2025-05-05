from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import pytz
from core import jira_client, utils
import logging
import os # Importa o módulo os para acessar variáveis de ambiente

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS (mantive, pois você já usava)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# COLABORADORES_INFO agora usa variáveis de ambiente para tokens sensíveis
COLABORADORES_INFO = {
    os.environ.get("COLABORADOR_1_ID", 'chave_default_1'): {'nome': "João", 'chamados': {f"{i}-{f}": [] for i, f in utils.FAIXAS}},
    os.environ.get("COLABORADOR_2_ID", 'chave_default_2'): {'nome': "Thiago", 'chamados': {f"{i}-{f}": [] for i, f in utils.FAIXAS}},
    os.environ.get("COLABORADOR_3_ID", 'chave_default_3'): {'nome': "Rodrigo", 'chamados': {f"{i}-{f}": [] for i, f in utils.FAIXAS}},
}

JQL = os.environ.get("JQL_CONSULTA", """
project = Tecnologia
AND status CHANGED TO "Aguardando Validação" AFTER startOfDay()
AND assignee IN ("712020:a8b4c6c4-c69d-4cfb-b6a2-6c9b6ab7fe8d", "712020:36b81325-6b27-4f7f-aaa9-d213ecc335c1", "712020:3bfbc6f6-915d-4f79-8feb-51063941bd7c")
""") #JQL também como variável de ambiente


@app.get("/chamados")
async def get_chamados():
    try:
        # Solicita o histórico de alterações para rastrear o tempo de resolução
        issues = jira_client.buscar_chamados(JQL, expand='changelog')
        logger.info(f"Retorno do jira_client.buscar_chamados: {issues}")  # Adicionado log

        dados = utils.classificar_chamados(issues, COLABORADORES_INFO)
        logger.info(f"Retorno do utils.classificar_chamados: {dados}")  # Adicionado log

        for issue_key, info in dados.items():
            # O erro ocorria porque 'issues' é uma lista de dicionários, não objetos.
            # Precisamos encontrar o dicionário correto na lista 'issues' usando a 'issue_key'.
            issue = next((iss for iss in issues if iss['key'] == issue_key), None)
            if not issue:
                logger.error(f"Issue com chave {issue_key} não encontrada após classificação.")
                # Vamos adicionar um log aqui para entender o porquê.
                logger.info(f"Chave procurada: {issue_key}")
                logger.info(f"Chaves encontradas no retorno do Jira: {[i['key'] for i in issues]}")
                continue  # Pula para a próxima issue se não for encontrada
            
            logger.info(f"Issue encontrada para a chave {issue_key}: {issue}") #ADICIONEI ESTE LOG

            reporter_name = issue.get('fields', {}).get('reporter', {}).get('displayName', "N/A")

            resolution_time = None
            opened_time = None
            validated_time = None

            for history in issue.get('changelog', {}).get('histories', []):
                for item in history.get('items', []):
                    if item.get('field') == 'status':
                        if item.get('toString') == 'Aberto':
                            opened_time = history.get('created')
                        elif item.get('toString') == 'Aguardando Validação':
                            validated_time = history.get('created')
                            break  # Já encontrou o status de validação, pode sair
                if validated_time:
                    break

            if opened_time and validated_time:
                try:
                    opened_dt = datetime.strptime(opened_time.split('+')[0], '%Y-%m-%dT%H:%M:%S.%f')
                    validated_dt = datetime.strptime(validated_time.split('+')[0], '%Y-%m-%dT%H:%M:%S.%f')
                    resolution_time = validated_dt - opened_dt
                except ValueError as e:
                    logger.error(f"Erro ao converter datas: {e} - opened: {opened_time}, validated: {validated_time}")
                    resolution_time = "N/A"

            # Garante que 'chamados' seja sempre uma lista de dicionários, mesmo que vazia
            info['chamados'] = info.get('chamados', {f"{i}-{f}": [] for i, f in utils.FAIXAS})
            for faixa, chamados_lista in info['chamados'].items():
                if issue: # só adiciona se a issue foi encontrada
                    # Garante que chamados_lista é uma lista. Se não for, cria uma lista vazia.
                    if not isinstance(chamados_lista, list):
                         chamados_lista = []
                    for chamado in chamados_lista:
                        chamado['reporter'] = reporter_name
                        chamado['tempo_resolucao'] = str(resolution_time) if resolution_time else "N/A"

        return {
            "ultima_atualizacao": datetime.now(pytz.timezone('America/Sao_Paulo')).strftime("%H:%M"),
            "dados": {
                info['nome']: info['chamados']
                for info in dados.values()
            }
        }
    except Exception as e:
        logger.error(f"Erro ao processar /chamados: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
