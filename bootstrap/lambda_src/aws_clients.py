####----------------------------------------------------------------------------------------####
####----                    Instancia os clientes AWS utilizados pela Lambda.           ----####
####----------------------------------------------------------------------------------------####

import boto3
from config import AWS_REGION

dynamodb = boto3.resource("dynamodb")
ssm      = boto3.client("ssm")
sns      = boto3.client("sns")
events   = boto3.client("events")
s3       = boto3.client("s3", region_name=AWS_REGION)