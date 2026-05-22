####---------------------------------------------####
####----  Compacta o código fonte da Lambda  ----####
####---------------------------------------------####
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/lambda_src/controle.py"
  output_path = "${path.module}/lambda_src/controle.zip"
}


####--------------------------------------------####
####----  Cria a função Lambda de controle  ----####
####--------------------------------------------####
resource "aws_lambda_function" "controle" {
  function_name    = "${var.app_name}-controle"
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  handler          = "controle.lambda_handler"
  runtime          = "python3.12"
  role             = aws_iam_role.lambda_control_role.arn
  timeout          = 30

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.control_table.name
      SNS_TOPIC_ARN  = aws_sns_topic.site_access_alerts.arn
      EVENTBRIDGE_RULE = "${var.app_name}-controle"
      SSM_SNS_ENABLED_PARAM = "/website-s3-iac-cv/enviar-sms"
      SSM_SITE_TIMEOUT_PARAM = "/website-s3-iac-cv/site-timeout-minutes"
    }
  }

  tags = {
    Project = var.app_name
  }
}

