####----------------------------------------------------------####
####----  Busca o Lambda de controle criado no bootstrap  ----####
####----------------------------------------------------------####
data "aws_lambda_function" "controle" {
  function_name = "${var.app_name}-controle"
}


####----------------------------------------------------------------####
####----  Cria a rule temporária do EventBridge                 ----####
####----  Existe somente enquanto o site efêmero estiver ativo  ----####
####----  A rule invoca o Lambda permanente de controle         ----####
####----------------------------------------------------------------####
resource "aws_cloudwatch_event_rule" "lifecycle" {
  name                = "${var.app_name}-controle"
  description         = "Agenda execução do Lambda de controle do ciclo de vida"
  schedule_expression = var.lifecycle_schedule
  state               = "ENABLED"
}


####----------------------------------------------------------------####
####----  Vincula o EventBridge à função Lambda **permanente**  ----####
####----------------------------------------------------------------####
resource "aws_cloudwatch_event_target" "lambda" {
  rule      = aws_cloudwatch_event_rule.lifecycle.name
  target_id = "${var.app_name}-lifecycle-lambda"
  arn       = data.aws_lambda_function.controle.arn
}


####------------------------------------------------------------------------####
####----  Permissão **temporária** para o EventBridge invocar o Lambda  ----####
####----  **permanente** de controle                                    ----####
####------------------------------------------------------------------------####
resource "aws_lambda_permission" "eventbridge" {
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = data.aws_lambda_function.controle.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.lifecycle.arn
}