####----------------------------------------------------------------------------------------####
####----          Define as constantes e variáveis de ambiente do website efêmero.      ----####
####----------------------------------------------------------------------------------------####

import os

TEMP_BUCKET = "TEMPORARIO"

CREATE_WORKFLOW = "apply.yml"
DESTROY_WORKFLOW = "destroy.yml"

DYNAMODB_TABLE = os.environ["DYNAMODB_TABLE"]

EVENTBRIDGE_RULE = os.environ.get("EVENTBRIDGE_RULE")

SSM_SITE_TIMEOUT_PARAM = os.environ["SSM_SITE_TIMEOUT_PARAM"]

SSM_SNS_ENABLED_PARAM = os.environ.get(
    "SSM_SNS_ENABLED_PARAM",
    "/website-s3-iac-cv/enviar-sms"
)

SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")

AWS_REGION = os.environ.get("AWS_REGION", "us-east-2")