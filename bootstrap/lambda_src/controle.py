####----------------------------------------------------------------------------------------####
####----  Lambda de controle do ciclo de vida do website efêmero.                       ----####
####----                                                                                ----####
####----  Regras principais:                                                            ----####
####----                                                                                ----####
####----  1. Quando chamada por usuário/API Gateway:                                    ----####
####----     - Envia alerta por e-mail via SNS.                                         ----####
####----     - Se o S3 ainda não existe, cria TEMPORARIO e dispara deploy no GitHub.    ----####
####----     - Se TEMPORARIO já existe, apenas retorna página de espera.                ----####
####----  - Se o S3 existe, atualiza last_accessed_at e serve o site via proxy S3.      ----####
####----                                                                                ----####
####----  2. Quando chamada pelo EventBridge:                                           ----####
####----     - Verifica last_accessed_at no DynamoDB.                                   ----####
####----     - Se passou o tempo configurado desde o último acesso, dispara destroy.    ----####
####----     - Se ainda não passou o tempo configurado, apenas reagenda o EventBridge.  ----####
####----                                                                                ----####
####----  Observação:                                                                   ----####
####----  - Destroy nunca é disparado por acesso de usuário/API Gateway.                ----####
####----  - Destroy só pode ser disparado quando a origem for EventBridge.              ----####
####----------------------------------------------------------------------------------------####

import boto3
import urllib3
import json
import os
from datetime import datetime, timezone, timedelta


TEMP_BUCKET = "TEMPORARIO"

CREATE_WORKFLOW = "apply.yml"
DESTROY_WORKFLOW = "destroy.yml"


def lambda_handler(event, context):
    print("=== Lambda controle iniciada ===")
    print("Evento recebido:")
    print(json.dumps(event, default=str))

    is_eventbridge = event.get("source") == "aws.events"

    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(os.environ["DYNAMODB_TABLE"])

    now = datetime.now(timezone.utc)

    print(f"Tabela DynamoDB: {os.environ['DYNAMODB_TABLE']}")
    print(f"Bucket temporário: {TEMP_BUCKET}")
    print(f"Origem EventBridge: {is_eventbridge}")

    if not is_eventbridge:
        _enviar_alerta_acesso(event, now)

    print("Buscando registros no DynamoDB...")

    response = table.scan()
    items = response.get("Items", [])

    print(f"Itens encontrados: {len(items)}")
    print(json.dumps(items, default=str))

    temp_item = next(
        (item for item in items if item["bucket_name"] == TEMP_BUCKET),
        None
    )

    active_items = [
        item
        for item in items
        if item["bucket_name"] != TEMP_BUCKET
    ]

    print(f"Registro TEMPORARIO encontrado: {temp_item is not None}")
    print(f"Ambientes ativos encontrados: {len(active_items)}")

    ####--------------------------------------------------------------------####
    ####----  CASO 1 E CASO 2 — chamada de usuário via API Gateway      ----####
    ####--------------------------------------------------------------------####
    if not is_eventbridge:
        print("Origem: usuário/API Gateway.")

        ####----------------------------------------------------------------####
        ####----  Usuário acessou, mas o S3 ainda não existe.            ----####
        ####----                                                        ----####
        ####----  Pode ser o primeiro acesso ou ambiente em criação.     ----####
        ####----                                                        ----####
        ####----  Regra:                                                ----####
        ####----  - cria TEMPORARIO, se ainda não existir               ----####
        ####----  - dispara workflow de criação no GitHub Actions       ----####
        ####----  - retorna página de espera                            ----####
        ####----  - não atualiza EventBridge                            ----####
        ####----------------------------------------------------------------####
        if not active_items:
            print("Nenhum S3 ativo encontrado.")

            if not temp_item:
                print("Nenhum TEMPORARIO encontrado.")
                print("Criando registro TEMPORARIO para indicar criação em andamento.")

                table.put_item(
                    Item={
                        "bucket_name": TEMP_BUCKET,
                        "created_at": now.isoformat(),
                        "last_accessed_at": now.isoformat()
                    }
                )

                print("Registro TEMPORARIO criado.")
                print("Disparando workflow de criação do ambiente efêmero...")

                _disparar_create()

                print("Workflow de criação acionado.")
            else:
                print("Ambiente já está em processo de criação.")

            print("Retornando página de espera.")
            print("Não atualiza last_accessed_at.")
            print("Não altera EventBridge.")

            return _html_carregando()

        ####----------------------------------------------------------------####
        ####----  Usuário acessou e o S3 existe.                        ----####
        ####----                                                        ----####
        ####----  Regra:                                                ----####
        ####----  - atualiza last_accessed_at com o horário atual       ----####
        ####----  - reagenda EventBridge para tempo configurado após    ----#### 
        ####----    este acesso                                         ----#### 
        ####----  - redireciona para o site estático no S3              ----####
        ####----  - nunca dispara destroy                               ----####
        ####----------------------------------------------------------------####
        item = active_items[0]
        bucket_name = item["bucket_name"]

        print(f"S3 ativo encontrado: {bucket_name}")
        print("Atualizando last_accessed_at no DynamoDB...")

        table.update_item(
            Key={"bucket_name": bucket_name},
            UpdateExpression="SET last_accessed_at = :ts",
            ExpressionAttributeValues={
                ":ts": now.isoformat()
            }
        )

        print(f"last_accessed_at atualizado para: {now.isoformat()}")

        timeout_minutes = _get_site_timeout_minutes()
        next_run = now + timedelta(minutes=timeout_minutes)

        print("Reagendando EventBridge conforme timeout configurado...")
        print(f"Próxima execução: {next_run.isoformat()}")

        _reagendar_eventbridge(next_run)

        print(f"Redirecionando usuário para o bucket: {bucket_name}")

        return _proxy_s3(bucket_name, event)

    ####--------------------------------------------------------------------####
    ####----  CASO 3 — chamada automática via EventBridge               ----####
    ####--------------------------------------------------------------------####
    print("Origem: EventBridge.")

    if not active_items:
        print("Nenhum S3 ativo encontrado.")
        print("Nada a destruir.")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "no_active_site"
            })
        }

    item = active_items[0]
    bucket_name = item["bucket_name"]

    last_accessed_at = datetime.fromisoformat(item["last_accessed_at"])

    if last_accessed_at.tzinfo is None:
        last_accessed_at = last_accessed_at.replace(tzinfo=timezone.utc)


    timeout_minutes = _get_site_timeout_minutes()
    expiration_time = last_accessed_at + timedelta(minutes=timeout_minutes)

    print(f"Bucket ativo: {bucket_name}")
    print(f"Último acesso: {last_accessed_at.isoformat()}")
    print(f"Horário atual: {now.isoformat()}")
    print(f"Horário de expiração: {expiration_time.isoformat()}")

    ####-------------------------------------------------------------------------####
    ####----  Se o último acesso ocorreu há menos que o tempo configurado o  ----####
    ####----  ambiente ainda deve permanecer ativo. Nesse caso, apenas .     ----####
    ####----  reagenda o EventBridge                                         ----####
    ####-------------------------------------------------------------------------####
    if now < expiration_time:
        print("Ainda não passou o tempo configurado desde o último acesso.")
        print("Reagendando EventBridge para o horário de expiração.")

        _reagendar_eventbridge(expiration_time)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "rescheduled",
                "bucket": bucket_name,
                "next_check": expiration_time.isoformat()
            })
        }

    ####--------------------------------------------------------------------####
    ####----  Passou mais que o tempo configurado sem acesso.           ----####
    ####----  Somente neste ponto o destroy pode ser disparado.         ----####
    ####--------------------------------------------------------------------####
    print("Tempo configurado sem acesso expirado.")
    print("Origem confirmada: EventBridge.")
    print("Disparando workflow destroy...")

    _disparar_destroy(bucket_name)

    print("Workflow destroy acionado.")
    print("Removendo item ativo do DynamoDB...")

    table.delete_item(
        Key={"bucket_name": bucket_name}
    )

    print("Item removido com sucesso.")

    return {
        "statusCode": 200,
        "body": json.dumps({
            "status": "triggered_destroy",
            "bucket": bucket_name
        })
    }


def _get_site_timeout_minutes():
    param_name = os.environ["SSM_SITE_TIMEOUT_PARAM"]
    valor = _get_ssm_parameter(param_name)
    minutos = int(valor)

    print(f"Timeout configurado: {minutos} minutos")

    return minutos


def _sns_habilitado():
    ####--------------------------------------------------------------------####
    ####----  Verifica se o envio de alerta SNS está habilitado.        ----####
    ####----  O valor é controlado pelo parâmetro SSM:                  ----####
    ####----  /website-s3-iac-cv/enviar-sms                             ----####
    ####----                                                            ----####
    ####----  true  = envia alerta via SNS                              ----####
    ####----  false = não envia alerta via SNS                          ----####
    ####--------------------------------------------------------------------####
    param_name = os.environ.get(
        "SSM_SNS_ENABLED_PARAM",
        "/website-s3-iac-cv/enviar-sms"
    )

    try:
        valor = _get_ssm_parameter(param_name)

        print(f"Parâmetro de controle SNS ({param_name}): {valor}")

        return valor.strip().lower() == "true"

    except Exception as erro:
        print("Erro ao consultar parâmetro de controle SNS.")
        print(str(erro))
        print("Por segurança, o envio SNS será bloqueado.")
        return False



def _enviar_alerta_acesso(event, now):
    ####--------------------------------------------------------------------####
    ####----  Envia alerta de acesso ao site por SNS.                    ----####
    ####----  Chamadas automáticas do EventBridge não geram e-mail.      ----####
    ####----                                                            ----####
    ####----  O envio é controlado pelo parâmetro SSM:                   ----####
    ####----  /website-s3-iac-cv/enviar-sms                             ----####
    ####--------------------------------------------------------------------####
    if not _sns_habilitado():
        print("Envio SNS desabilitado via SSM. Alerta de acesso ignorado.")
        return

    topic_arn = os.environ.get("SNS_TOPIC_ARN")

    if not topic_arn:
        print("SNS_TOPIC_ARN não definida. Alerta de acesso ignorado.")
        return

    try:
        sns = boto3.client("sns")

        request_context = event.get("requestContext", {})
        http_context = request_context.get("http", {})

        source_ip = http_context.get("sourceIp", "desconhecido")
        method = http_context.get("method", "desconhecido")
        user_agent = http_context.get("userAgent", "desconhecido")

        headers = event.get("headers", {}) or {}
        referer = headers.get("referer", headers.get("Referer", "desconhecido"))

        path = event.get("rawPath", event.get("path", "desconhecido"))

        message = f"""
Acesso detectado no website efêmero.

Data/hora UTC: {now.isoformat()}
IP de origem: {source_ip}
Método: {method}
Path: {path}
User-Agent: {user_agent}
Referer: {referer}
"""

        sns.publish(
            TopicArn=topic_arn,
            Subject="Acesso ao website efêmero",
            Message=message
        )

        print("Alerta de acesso enviado por SNS.")

    except Exception as erro:
        print("Erro ao enviar alerta por SNS.")
        print(str(erro))


def _html_carregando():
    print("Retornando página HTML de carregamento.")
    return _waiting_page()


def _proxy_s3(bucket_name, event):
    path = event.get("rawPath", "/")
    key = path.lstrip("/") or "index.html"

    s3 = boto3.client("s3", region_name=os.environ.get("AWS_REGION", "us-east-2"))

    try:
        obj = s3.get_object(Bucket=bucket_name, Key=key)
        body = obj["Body"].read()
        content_type = obj.get("ContentType", "text/html; charset=utf-8")

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": content_type,
                "Cache-Control": "no-store"
            },
            "body": body.decode("utf-8")
        }
    except Exception as e:
        print(f"Erro ao buscar objeto S3: {str(e)}")
        # Fallback para index.html
        obj = s3.get_object(Bucket=bucket_name, Key="index.html")
        body = obj["Body"].read()
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "text/html; charset=utf-8"},
            "body": body.decode("utf-8")
        }




def _waiting_page():
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "text/html; charset=utf-8",
            "Cache-Control": "no-store"
        },
        "body": """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="10">

    <meta
        http-equiv="Cache-Control"
        content="no-cache, no-store, must-revalidate"
    >
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">

    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portfólio sob demanda</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 760px;
            margin: 80px auto;
            padding: 0 24px;
            line-height: 1.6;
            color: #333;
        }

        h1 {
            color: #111;
            margin-bottom: 24px;
        }

        .spinner {
            width: 32px;
            height: 32px;
            border: 4px solid #e5e5e5;
            border-top: 4px solid #333;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 30px 0;
        }

        @keyframes spin {
            to {
                transform: rotate(360deg);
            }
        }

        a {
            color: #0a66c2;
            text-decoration: none;
        }

        a:hover {
            text-decoration: underline;
        }

        .note {
            margin-top: 32px;
            font-size: 0.95rem;
            color: #666;
        }
    </style>
</head>
<body>
    <h1>Portfólio sendo preparado</h1>

    <p>
        Este site é disponibilizado sob demanda.
    </p>

    <p>
        Quando alguém acessa o portfólio, o ambiente é iniciado automaticamente.
        Esse processo pode levar cerca de um minuto.
    </p>

    <p>
        Assim que estiver pronto, você será redirecionado automaticamente
        para o site.
    </p>

    <div class="spinner"></div>

    <p class="note">
        Se quiser entender a arquitetura por trás desta solução,
        a explicação completa está no
        <a
            href="https://github.com/carlafs1/website-s3-iac-cv"
            target="_blank"
            rel="noopener noreferrer"
        >
            README do projeto
        </a>.
    </p>
</body>
</html>
"""
    }


def _get_ssm_parameter(name, with_decryption=False):
    print(f"Lendo parâmetro SSM: {name}")

    ssm = boto3.client("ssm")

    result = ssm.get_parameter(
        Name=name,
        WithDecryption=with_decryption
    )

    print(f"Parâmetro {name} obtido com sucesso.")

    return result["Parameter"]["Value"]


def _get_github_config():
    ###########################################################################
    ################      OBTÉM CONFIGURAÇÕES DO GITHUB NO SSM      ###########
    ###########################################################################
    # Recupera do AWS Systems Manager Parameter Store:
    # - /website/github/token: token usado para autenticar na API do GitHub.
    # - /website/github/repo : repositório no formato "usuario/repositorio".
    #
    # Esses valores não ficam como variáveis de ambiente da Lambda.
    ###########################################################################

    print("Obtendo token do GitHub no Parameter Store...")

    token = _get_ssm_parameter(
        "/website/github/token",
        with_decryption=True
    )

    print("Obtendo nome do repositório...")

    repo = _get_ssm_parameter(
        "/website/github/repo"
    )

    print(f"Repositório: {repo}")

    return token, repo


def _disparar_workflow(workflow_name, inputs=None):
    token, repo = _get_github_config()

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


def _disparar_create():
    _disparar_workflow(CREATE_WORKFLOW)


def _disparar_destroy(bucket_name):
    _disparar_workflow(DESTROY_WORKFLOW)


def _reagendar_eventbridge(next_run):
    print("Iniciando reagendamento do EventBridge...")

    events = boto3.client("events")
    rule = os.environ.get("EVENTBRIDGE_RULE")

    if not rule:
        print("EVENTBRIDGE_RULE não definida. Reagendamento ignorado.")
        return


    expression = (
        f"cron({next_run.minute} "
        f"{next_run.hour} "
        f"{next_run.day} "
        f"{next_run.month} "
        f"? "
        f"{next_run.year})"
    )

    print(f"Rule: {rule}")
    print(f"Próxima execução: {next_run.isoformat()}")
    print(f"Nova expressão cron: {expression}")

    events.put_rule(
        Name=rule,
        ScheduleExpression=expression,
        State="ENABLED"
    )

    print("EventBridge reagendado com sucesso.")