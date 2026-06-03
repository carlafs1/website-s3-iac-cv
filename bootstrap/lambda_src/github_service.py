####----------------------------------------------------------------------------------------####
####----           Aciona workflows de APPLY e DESTROY da infraestrutura efêmera        ----####
####----------------------------------------------------------------------------------------####

import json
import urllib3

from config import (
    CREATE_WORKFLOW, 
    DESTROY_WORKFLOW
)
from parameters import get_ssm_parameter


# Busca nome do repositório e token do Github para permitir acesso aos workflows
def get_github_config():
    print("Obtendo token e ropositório do GitHub no Parameter Store.")
    token = get_ssm_parameter(
        "/website/github/token",
        with_decryption=True
    )

    repo = get_ssm_parameter("/website/github/repo")
    print(f"Repositório: {repo}")

    return token, repo


# Executa o workflow
def dispatch_workflow(workflow_name, inputs=None):
    token, repo = get_github_config()
    http = urllib3.PoolManager()

    url = (
        f"https://api.github.com/repos/"
        f"{repo}/actions/workflows/{workflow_name}/dispatches"
    )

    payload_data = {
        "ref": "main"
    }

    if inputs:
        payload_data["inputs"] = inputs

    payload = json.dumps(payload_data).encode("utf-8")
    print(f"Disparando workflow: {workflow_name}")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload_data)}")

    response = http.request(
        "POST",
        url,
        body=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json"
        }
    )

    print(f"GitHub retornou status {response.status}")

    if response.status not in (204, 201):
        raise Exception(
            f"Erro ao disparar workflow {workflow_name}. "
            f"HTTP {response.status}: "
            f"{response.data.decode('utf-8')}"
        )

    print(f"Workflow {workflow_name} disparado com sucesso.")


def dispatch_create():
    dispatch_workflow(CREATE_WORKFLOW)


def dispatch_destroy():
    # Se o destroy.yml não aceitar inputs, remova o parâmetro inputs abaixo
    # e use apenas: dispatch_workflow(DESTROY_WORKFLOW)
    dispatch_workflow(DESTROY_WORKFLOW)
