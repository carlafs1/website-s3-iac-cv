####----------------------------------------------------------------------------------------####
####----  Lambda de controle do ciclo de vida do website efêmero.                       ----####
####----                                                                                ----####
####----  Regras principais:                                                            ----####
####----                                                                                ----####
####----  1. Quando chamada por usuário/API Gateway:                                    ----####
####----     - Envia alerta por e-mail via SNS.                                         ----####
####----     - Se o S3 ainda não existe, cria TEMPORARIO e dispara deploy no GitHub.    ----####
####----     - Se TEMPORARIO já existe, apenas retorna página de espera.                ----####
####----     - Se o S3 existe, serve o site via proxy S3.                               ----####
####----     - Se o acesso for confiável, atualiza last_accessed_at e reagenda timeout. ----####
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

import json
from datetime import datetime, timezone, timedelta

from dynamodb_service import (
    scan_lifecycle_items,
    split_items,
    create_temp_item,
    update_last_accessed,
    delete_bucket_item,
)
from eventbridge_service import reschedule_eventbridge
from github_service import dispatch_create, dispatch_destroy
from html_pages import waiting_page, scanner_ignored_page, error_page
from notification_service import send_access_alert, send_destroy_error_alert
from parameters import get_site_timeout_minutes
from s3_service import bucket_exists, proxy_s3
from security import is_trusted_access


def lambda_handler(event, context):
    print("=== Lambda controle iniciada ===")
    print("Evento recebido:")
    print(json.dumps(event, default=str))

    now = datetime.now(timezone.utc)
    is_eventbridge = event.get("source") == "aws.events"

    if not is_eventbridge:
        send_access_alert(event, now)

    items = scan_lifecycle_items()
    temp_item, active_items = split_items(items)

    print(json.dumps({
        "event": "lambda_execution",
        "timestamp": now.isoformat(),
        "origem_eventbridge": is_eventbridge,
        "temp_item": bool(temp_item),
        "active_items": len(active_items),
        "bucket": active_items[0]["bucket_name"] if active_items else None
    }))

    if not is_eventbridge:
        return handle_user_access(
            event=event,
            now=now,
            temp_item=temp_item,
            active_items=active_items
        )

    return handle_eventbridge(
        now=now,
        active_items=active_items
    )


def handle_user_access(event, now, temp_item, active_items):
    print("Origem: usuário/API Gateway.")

    if not active_items:
        print("Nenhum S3 ativo encontrado.")

        if not is_trusted_access(event):
            print(json.dumps({
                "event": "access_rejected",
                "reason": "scanner_or_untrusted",
                "timestamp": now.isoformat()
            }))
            return scanner_ignored_page()

        if not temp_item:
            create_temp_item(now)
            dispatch_create()
            print(json.dumps({
                "event": "deploy_triggered",
                "reason": "no_active_s3_no_temp_item",
                "timestamp": now.isoformat()
            }))
        else:
            print("Ambiente já está em processo de criação.")

        print("Retornando página de espera.")
        return waiting_page()

    item = active_items[0]
    bucket_name = item["bucket_name"]

    print(f"S3 ativo encontrado: {bucket_name}")

    # Segunda chamada — contexto diferente: S3 já está ativo.
    # Aqui a decisão não é sobre acordar o ambiente,
    # mas sobre renovar ou não o ciclo de vida

    trusted_access = is_trusted_access(event)

    if trusted_access:
        update_last_accessed(bucket_name, now)

        timeout_minutes = get_site_timeout_minutes()
        next_run = (now + timedelta(minutes=timeout_minutes)).replace(
            second=0,
            microsecond=0
        )

        print(f"Reagendando EventBridge. Próxima execução: {next_run.isoformat()}")
        reschedule_eventbridge(next_run)

    else:
        print(json.dumps({
            "event": "active_site_untrusted_access",
            "reason": "served_without_extending_lifetime",
            "bucket": bucket_name,
            "timestamp": now.isoformat()
        }))
        print("Acesso não confiável com S3 ativo. Servindo site sem renovar last_accessed_at.")

    print(f"Servindo site via proxy S3. Bucket: {bucket_name}")

    try:
        return proxy_s3(bucket_name, event)

    except Exception as erro:
        print(json.dumps({
            "event": "proxy_s3_error",
            "bucket": bucket_name,
            "bucket_exists": bucket_exists(bucket_name),
            "error": str(erro),
            "timestamp": now.isoformat()
        }))

        if not bucket_exists(bucket_name):
            print("Bucket desapareceu durante o acesso. Removendo item órfão.")
            delete_bucket_item(bucket_name)

        return error_page(
            "O ambiente do portfólio está sendo sincronizado. "
            "A página será atualizada automaticamente."
        )


def handle_eventbridge(now, active_items):
    print("Origem: EventBridge.")

    if not active_items:
        print("Nenhum ambiente ativo encontrado. Nada a destruir ou reagendar.")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "no_active_environment"
            })
        }

    item = active_items[0]
    bucket_name = item["bucket_name"]

    last_accessed_at = datetime.fromisoformat(item["last_accessed_at"])

    if last_accessed_at.tzinfo is None:
        last_accessed_at = last_accessed_at.replace(tzinfo=timezone.utc)

    timeout_minutes = get_site_timeout_minutes()

    now = now.replace(second=0, microsecond=0)
    last_accessed_at = last_accessed_at.replace(second=0, microsecond=0)

    expiration_time = last_accessed_at + timedelta(minutes=timeout_minutes)

    print(f"Bucket ativo: {bucket_name}")
    print(f"Último acesso: {last_accessed_at.isoformat()}")
    print(f"Horário atual: {now.isoformat()}")
    print(f"Horário de expiração: {expiration_time.isoformat()}")

    if now < expiration_time:
        print("Ainda dentro do timeout. Reagendando EventBridge.")
        reschedule_eventbridge(expiration_time)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "rescheduled",
                "bucket": bucket_name,
                "next_check": expiration_time.isoformat()
            })
        }

    print("Timeout expirado. Disparando workflow destroy.")

    try:
        dispatch_destroy()
        delete_bucket_item(bucket_name)
        print(json.dumps({
            "event": "destroy_triggered",
            "bucket": bucket_name,
            "last_accessed_at": last_accessed_at.isoformat(),
            "expiration_time": expiration_time.isoformat(),
            "timestamp": now.isoformat()
        }))

    except Exception as erro:
        print(json.dumps({
            "event": "destroy_error",
            "bucket": bucket_name,
            "error": str(erro),
            "timestamp": now.isoformat()
        }))

        send_destroy_error_alert(
            bucket_name=bucket_name,
            error_message=str(erro),
            now=now
        )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "status": "triggered_destroy",
            "bucket": bucket_name
        })
    }