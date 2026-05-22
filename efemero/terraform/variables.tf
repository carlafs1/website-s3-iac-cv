
####-------------------------------------------####
#####----  Define região AWS dos recursos  ----####
####-------------------------------------------####
variable "aws_region" {
  description = "Região da AWS para implantar os recursos"
  type        = string
  default     = "us-east-2"
}


####-------------------------------####
#####----  Define nome da APP  ----####
####-------------------------------####
variable "app_name" {
  description = "Nome base utilizado na composição dos nomes dos recursos"
  type        = string
  default     = "website-s3-iac-cv"
}


####-----------------------------------####
#####----  Nome da tabela DynamoDB ----####
####-----------------------------------####
variable "dynamodb_table_name" {
  description = "Nome da tabela DynamoDB permanente criada no bootstrap"
  type        = string
  default     = "website-lifecycle-control"
}


####-------------------------------------------------------------------####
#####----  Frequência inicial de execução da regra do EventBridge  ----####
####-------------------------------------------------------------------####
variable "lifecycle_schedule" {
  description = "Expressão cron do EventBridge para monitorar o ciclo de vida do ambiente"
  type        = string
  default     = "rate(1 hour)"
}