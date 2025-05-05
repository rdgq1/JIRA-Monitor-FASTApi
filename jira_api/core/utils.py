# core/utils.py
from datetime import datetime
import pytz
import logging

logger = logging.getLogger(__name__)

TIMEZONE = pytz.timezone('America/Sao_Paulo')
FAIXAS = [(8, 9), (9, 10), (10, 11), (11, 12), (12, 15), (15, 16), (16, 17), (17, 18)]

def classificar_chamados(issues: list, colaboradores_info: dict) -> dict:
    """Classifica chamados por colaborador e faixa de hora."""

    for account_id in colaboradores_info:
        for faixa in colaboradores_info[account_id]['chamados']:
            colaboradores_info[account_id]['chamados'][faixa] = []

    for issue in issues:
        assignee = issue.get('fields', {}).get('assignee')
        if not assignee:
            continue

        assignee_id = assignee.get('accountId')
        if assignee_id not in colaboradores_info:
            continue

        for hist in issue.get('changelog', {}).get('histories', []):
            for item in hist.get('items', []):
                if item.get('field') == 'status' and item.get('toString', '').lower() == 'aguardando validação':
                    created_str = hist.get('created')
                    if created_str:
                        if isinstance(created_str, datetime):
                            dt = created_str.astimezone(TIMEZONE)
                        else:
                            dt = datetime.strptime(created_str.split('+')[0], "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=pytz.utc).astimezone(TIMEZONE)
                        for inicio, fim in FAIXAS:
                            if inicio <= dt.hour < fim:
                                faixa_label = f"{inicio}-{fim}"
                                colaboradores_info[assignee_id]['chamados'][faixa_label].append(f"{issue['key']}: {issue.get('fields', {}).get('summary')}")
                                break
                    else:
                        logger.warning(f"hist['created'] is None for issue {issue.get('key')}")
                    break
            else:
                continue
            break
    return colaboradores_info
