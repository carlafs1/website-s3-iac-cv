###------------------------------------------------####
####----  Busca a role IAM criada no bootstrap  ----####
####------------------------------------------------####
data "aws_iam_role" "lambda_acesso_role" {
  name = "${var.app_name}-acesso-lambda-role"
}


####-------------------------------------------------------####
####----  Compacta o código fonte do Lambda de acesso  ----####
####-------------------------------------------------------####
data "archive_file" "lambda_acesso_zip" {
  type        = "zip"
  source_file = "${path.module}/lambda_src/registro_bucket.py"
  output_path = "${path.module}/lambda_src/.terraform/tmp/registro_bucket.zip"
}


####------------------------------------------####
####----  Cria a função Lambda de acesso  ----####
####------------------------------------------####
resource "aws_lambda_function" "acesso" {
  function_name    = "${var.app_name}-acesso"
  filename         = data.archive_file.lambda_acesso_zip.output_path
  source_code_hash = data.archive_file.lambda_acesso_zip.output_base64sha256
  handler          = "registro_bucket.lambda_handler"
  runtime          = "python3.12"
  role             = data.aws_iam_role.lambda_acesso_role.arn
  timeout          = 30

  environment {
    variables = {
      DYNAMODB_TABLE = var.dynamodb_table_name
      BUCKET_NAME    = aws_s3_bucket.app_bucket.bucket
    }
  }
}
