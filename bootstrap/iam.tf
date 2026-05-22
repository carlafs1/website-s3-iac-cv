###########################################################################
################              B O O T S T R A P            ################
###########################################################################


####-------------------------------------------------####
####----  Role assumida pela Lambda de controle  ----####
####-------------------------------------------------####
resource "aws_iam_role" "lambda_control_role" {
  name = "${var.app_name}-lifecycle-control-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}


####--------------------------------------------------------------------####
####----  Permissões da Lambda de controle para acessar o DynamoDB  ----####
####--------------------------------------------------------------------####
resource "aws_iam_role_policy" "control_dynamodb" {
  name = "${var.app_name}-lifecycle-control-dynamodb-policy"
  role = aws_iam_role.lambda_control_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "dynamodb:Scan",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem"
      ]
      Resource = aws_dynamodb_table.control_table.arn
    }]
  })
}


####-----------------------------------------------------------------------####
####----  Permissões da Lambda de controle para ler parâmetros no SSM  ----####
####-----------------------------------------------------------------------####
data "aws_caller_identity" "current" {}

resource "aws_iam_role_policy" "control_ssm" {
  name = "${var.app_name}-lifecycle-control-ssm-policy"
  role = aws_iam_role.lambda_control_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter"
        ]
        Resource = [
          "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/website/github/token",
          "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/website/github/repo", 
          "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/website-s3-iac-cv/enviar-sms",
          "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/website-s3-iac-cv/site-timeout-minutes"
        ]
      }
    ]
  })
}


####-------------------------------------------------------------------------------####
####----  Permissões da Lambda de controle para reagendar o EventBridge        ----####
####-------------------------------------------------------------------------------####
resource "aws_iam_role_policy" "control_eventbridge" {
  name = "${var.app_name}-lifecycle-control-eventbridge-policy"
  role = aws_iam_role.lambda_control_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "events:PutRule"
      ]
      Resource = "arn:aws:events:${var.aws_region}:*:rule/${var.app_name}-*"
    }]
  })
}


####------------------------------------------------------------------####
####----  Permissões básicas de log para a Lambda de controle     ----####
####------------------------------------------------------------------####
resource "aws_iam_role_policy_attachment" "control_basic_execution" {
  role       = aws_iam_role.lambda_control_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}


####---------------------------------------------------------------####
####----  Permite que a Lambda de controle publique no SNS     ----####
####---------------------------------------------------------------####
resource "aws_iam_role_policy" "controle_sns_publish" {
  name = "${var.app_name}-controle-sns-publish-policy"
  role = aws_iam_role.lambda_control_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "sns:Publish"
      ]
      Resource = aws_sns_topic.site_access_alerts.arn
    }]
  })
}


####------------------------------------------------------------------####
####----  Permissões da Lambda de controle para ler o bucket S3    ----####
####------------------------------------------------------------------####
resource "aws_iam_role_policy" "control_s3_read" {
  name = "${var.app_name}-lifecycle-control-s3-read-policy"
  role = aws_iam_role.lambda_control_role.id 

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid    = "ReadTfstateS3"
      Effect = "Allow"
      Action = [
        "s3:GetObject",
        "s3:ListBucket"
      ]
      Resource = [
        "arn:aws:s3:::website-s3-iac-cv-tfstate",
        "arn:aws:s3:::website-s3-iac-cv-tfstate/*"
      ]
    }]
  })
}


###########################################################################
################                E F E M E R O              ################
###########################################################################


####-----------------------------------------------####
####----  Role assumida pela Lambda de acesso  ----####
####-----------------------------------------------####
resource "aws_iam_role" "lambda_acesso_role" {
  name = "${var.app_name}-acesso-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}


####-------------------------------------------------------------------####
####----  Permissões da Lambda de acesso para acessar o DynamoDB   ----####
####-------------------------------------------------------------------####
resource "aws_iam_role_policy" "acesso_dynamodb" {
  name = "${var.app_name}-acesso-dynamodb-policy"
  role = aws_iam_role.lambda_acesso_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "dynamodb:PutItem",
        "dynamodb:DeleteItem"
      ]
      Resource = aws_dynamodb_table.control_table.arn
    }]
  })
}


####------------------------------------------------------------------####
####----  Permissões básicas de log para a Lambda de acesso       ----####
####------------------------------------------------------------------####
resource "aws_iam_role_policy_attachment" "acesso_basic_execution" {
  role       = aws_iam_role.lambda_acesso_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

