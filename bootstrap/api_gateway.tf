####-----------------------------------------------------####
####----  Cria a API HTTP para entrada da aplicação  ----####
####-----------------------------------------------------####
resource "aws_apigatewayv2_api" "http_api" {
  name          = "${var.app_name}-api"
  protocol_type = "HTTP"

  tags = {
    Project = var.app_name
  }
}


####----------------------------------------------------------####
####----  Integra a API Gateway com a Lambda de controle  ----####
####----------------------------------------------------------####
resource "aws_apigatewayv2_integration" "lambda_control" {
  api_id                 = aws_apigatewayv2_api.http_api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.controle.invoke_arn
  payload_format_version = "2.0"
}


####-------------------------------------------####
####----  Cria a rota raiz da API Gateway  ----####
####-------------------------------------------####
resource "aws_apigatewayv2_route" "root" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_control.id}"
}


####----------------------------------------------####
####----  Cria o stage padrão da API Gateway  ----####
####----------------------------------------------####
resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "$default"
  auto_deploy = true

  tags = {
    Project = var.app_name
  }
}


####---------------------------------------------------------------####
####----  Permite que a API Gateway invoque a Lambda controle  ----####
####---------------------------------------------------------------####
resource "aws_lambda_permission" "allow_api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.controle.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}