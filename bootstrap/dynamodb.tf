####------------------------------------------------------------------####
####----  Cria a tabela DynamoDB para controle do ciclo de vida   ----####
####------------------------------------------------------------------####
resource "aws_dynamodb_table" "control_table" {
  name         = "website-lifecycle-control"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "bucket_name"

  attribute {
    name = "bucket_name"
    type = "S"
  }

  tags = {
    Project = var.app_name
    Purpose = "website-lifecycle-control"
  }
}