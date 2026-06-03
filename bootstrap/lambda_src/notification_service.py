####----------------------------------------------------------------------------------------####
####----                   Envia notificação para cada novo acesso ao site.             ----####
####----------------------------------------------------------------------------------------####
####----                                                                                ----####
####----  SSM_SNS_ENABLED_PARAM : Indica se deve ou não enviar mensagem para novos      ----####
####----                          acesso ao site.                                       ----####
####----  O envio de e-mail é parametrizado no AWS Systems Manager -> Repositório de    ----####
####----  parâmetros -> /website-s3-iac-cv/enviar-sms                                   ----####
####----                                                                                ----####
####----------------------------------------------------------------------------------------####

from aws_clients import sns
from config import SNS_TOPIC_ARN
from parameters import get_sns_enabled

def send_access_alert(event, now):
    if not get_sns_enabled():
        print("Envio SNS desabilitado via SSM. Alerta de acesso ignorado.")
        return

    if not SNS_TOPIC_ARN:
        print("SNS_TOPIC_ARN não definida. Alerta de acesso ignorado.")
        return

    try:
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
            TopicArn=SNS_TOPIC_ARN,
            Subject="Acesso ao website efêmero",
            Message=message
        )
        print("Alerta de acesso enviado por SNS.")

    except Exception as erro:
        print("Erro ao enviar alerta por SNS.")
        print(str(erro))