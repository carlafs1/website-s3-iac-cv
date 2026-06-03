####----------------------------------------------------------------------------------------####
####----                          Seleciona parâmetros do processo                      ----####
####----------------------------------------------------------------------------------------####
####----                                                                                ----####
####----  SSM_SNS_ENABLED_PARAM : Indica se deve ou não enviar mensagem para novos      ----####
####----                          acesso ao site.                                       ----####
####----  SSM_SITE_TIMEOUT_PARAM: Tempo parametrizado para que o site seja destruído ou ----####
####----                          reagendado.                                           ----####
####----                                                                                ----####
####----------------------------------------------------------------------------------------####

from aws_clients import ssm
from config import (
	SSM_SITE_TIMEOUT_PARAM, 
	SSM_SNS_ENABLED_PARAM
)

def get_ssm_parameter(name, with_decryption=False):
    print(f"Lendo parâmetro SSM: {name}")

    result = ssm.get_parameter(
        Name=name,
        WithDecryption=with_decryption
    )

    print(f"Parâmetro {name} obtido com sucesso.")

    return result["Parameter"]["Value"]


def get_site_timeout_minutes():
    valor = get_ssm_parameter(SSM_SITE_TIMEOUT_PARAM)
    minutos = int(valor)

    print(f"Timeout configurado: {minutos} minutos")

    return minutos


def get_sns_enabled():
    valor = get_ssm_parameter(SSM_SNS_ENABLED_PARAM)
    return valor.strip().lower() == "true"
