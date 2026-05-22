####--------------------------------------------####
####----  Define a região AWS dos recursos  ----####
####--------------------------------------------####
variable "aws_region" {
  description = "Região da AWS para implantar os recursos"
  type        = string
  default     = "us-east-2"
}


####--------------------------------------####
####----  Define o nome da aplicação  ----####
####--------------------------------------####
variable "app_name" {
  description = "Nome base para os recursos"
  type        = string
  default     = "website-s3-iac-cv"
}

