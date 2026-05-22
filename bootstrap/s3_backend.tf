####---------------------------------------------------####
####----  Bucket S3 para armazenar Terraform State ----####
####---------------------------------------------------####
resource "aws_s3_bucket" "terraform_state" {
  bucket = "website-s3-iac-cv-tfstate"

  force_destroy = false

  tags = {
    Project = var.app_name
  }
}


####-------------------------------------------------------------------####
####----  Bloqueia acesso público do bucket de Terraform State      ----####
####-------------------------------------------------------------------####
resource "aws_s3_bucket_public_access_block" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = true
  restrict_public_buckets = true
}