####----------------------------------------------------------------------------------------####
####----             CRUD da tabela website-lifecycle-control no DynamoDB               ----####
####----------------------------------------------------------------------------------------####

import json
from aws_clients import dynamodb
from config import DYNAMODB_TABLE, TEMP_BUCKET


table = dynamodb.Table(DYNAMODB_TABLE)


# Busca registros na tabela 
def scan_lifecycle_items():
    print("Buscando registros no DynamoDB...")

    response = table.scan()
    items = response.get("Items", [])

    print(f"Itens encontrados: {len(items)}")
    print(json.dumps(items, default=str))

    return items

# Verifica se bucket efêmero já está cadastrado
def split_items(items):
    temp_item = next(
        (item for item in items if item.get("bucket_name") == TEMP_BUCKET),
        None
    )

    active_items = [
        item
        for item in items
        if item.get("bucket_name") != TEMP_BUCKET
    ]

    print(f"Registro TEMPORARIO encontrado: {temp_item is not None}")
    print(f"Ambientes ativos encontrados: {len(active_items)}")

    return temp_item, active_items


# Cria registro temporário caso o site não tenha sido criado ainda
def create_temp_item(now):
    print("Criando registro TEMPORARIO no DynamoDB.")

    table.put_item(
        Item={
            "bucket_name": TEMP_BUCKET,
            "created_at": now.isoformat(),
            "last_accessed_at": now.isoformat()
        }
    )

    print("Registro TEMPORARIO criado.")


# Atualiza last_update para controlar reagendamento do site caso haja novo acesso com o site já criado, 
# evitando criação de bucket em duplicidade
def update_last_accessed(bucket_name, now):
    print(f"Atualizando last_accessed_at para bucket: {bucket_name}")

    table.update_item(
        Key={"bucket_name": bucket_name},
        UpdateExpression="SET last_accessed_at = :ts",
        ExpressionAttributeValues={
            ":ts": now.isoformat()
        }
    )

    print(f"last_accessed_at atualizado para: {now.isoformat()}")


# Remove registro da tabela após destroy ou ao detectar item órfão
def delete_bucket_item(bucket_name):
    print(f"Removendo item do DynamoDB: {bucket_name}")

    table.delete_item(
        Key={"bucket_name": bucket_name}
    )

    print("Item removido com sucesso.")
