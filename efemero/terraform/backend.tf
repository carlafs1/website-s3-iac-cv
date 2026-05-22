####---------------------------------------------------------####
####----  Backend remoto para o Terraform State no S3    ----####
####---------------------------------------------------------####
terraform {
  backend "s3" {
    bucket = "website-s3-iac-cv-tfstate"
    key    = "efemero/terraform.tfstate"
    region = "us-east-2"
  }
}