####------------------------------------------------------####
#####----  Define os provedores que serão instalados  ----####
####------------------------------------------------------####
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0" 
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}


####-----------------------------------------------------------####
#####----  Do provedor AWS define a região que será usada  ----####
####-----------------------------------------------------------####
provider "aws" {
  region = var.aws_region
}