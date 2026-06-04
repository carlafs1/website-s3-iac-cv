####------------------------------------------------------------------------------------####
####----  Lambda de acesso do ambiente efêmero.                                      ----####
####----                                                                                ----####
####----  Esta Lambda é chamada pelo fluxo de criação do ambiente efêmero, após o     ----####
####----  Terraform criar o bucket S3 do site estático.                              ----####
####----                                                                                ----####
####----  Regras principais:                                                         ----####
####----                                                                                ----####
####----  1. Recebe o nome do bucket S3 criado.                                      ----####
####----  2. Cria o registro definitivo no DynamoDB.                                 ----####
####----  3. Define created_at e last_accessed_at com o horário atual.               ----####
####----  4. Remove o registro TEMPORARIO, pois o ambiente deixou de estar em        ----####
####----     criação e passou a estar disponível.                                    ----####
####----                                                                                ----####
####----  Observação:                                                                 ----####
####----  - Esta Lambda não controla expiração.                                      ----####
####----  - Esta Lambda não agenda EventBridge.                                      ----####
####----  - Esta Lambda não dispara destroy.                                         ----####
####----  - O controle de acesso, renovação de tempo e destroy fica no controle.py.  ----####
####------------------------------------------------------------------------------------####

import boto3
import json
import os
from datetime import datetime, timezone


TEMP_BUCKET = "TEMPORARIO"


def lambda_handler(event, context):
    print("=== Lambda acesso iniciada ===")
    print("Evento recebido:")
    print(json.dumps(event, default=str))

    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(os.environ["DYNAMODB_TABLE"])

    now = datetime.now(timezone.utc).isoformat()

    try:
        # ------------------------------------------------------------------
        # O bucket_name deve ser enviado pelo fluxo de criação do ambiente
        # efêmero, normalmente após o Terraform criar o bucket S3.
        # ------------------------------------------------------------------
        bucket_name = os.environ.get("BUCKET_NAME")

        if not bucket_name:
            raise ValueError("bucket_name não foi informado no evento.")

        print(f"Bucket recebido: {bucket_name}")

        # ------------------------------------------------------------------
        # Cria o registro definitivo do ambiente ativo.
        #
        # A partir deste momento, o controle.py passa a reconhecer que
        # o site estático já existe.
        #
        # created_at:
        # - marca quando o ambiente ficou disponível.
        #
        # last_accessed_at:
        # - inicia com o mesmo horário, pois este é o primeiro momento em
        #   que o ambiente pode ser considerado acessível.
        # ------------------------------------------------------------------
        print("Criando registro definitivo no DynamoDB...")

        table.put_item(
            Item={
                "bucket_name": bucket_name,
                "created_at": now,
                "last_accessed_at": now
            }
        )

        print("Registro definitivo criado com sucesso.")
        print(f"created_at: {now}")
        print(f"last_accessed_at: {now}")

        # ------------------------------------------------------------------
        # Remove o registro TEMPORARIO.
        #
        # TEMPORARIO indica que o ambiente estava em criação.
        # Depois que o bucket definitivo foi registrado, esse marcador
        # não é mais necessário.
        # ------------------------------------------------------------------
        print("Removendo registro TEMPORARIO...")

        table.delete_item(
            Key={
                "bucket_name": TEMP_BUCKET
            }
        )

        print("Registro TEMPORARIO removido com sucesso.")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "bucket_registered",
                "bucket_name": bucket_name,
                "created_at": now,
                "last_accessed_at": now
            })
        }

    except Exception as e:
        print(f"Erro na Lambda acesso: {str(e)}")

        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e)
            })
        }