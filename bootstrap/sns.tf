####------------------------------------------------------------####
####----  Cria o tópico SNS para alertas de acesso ao site  ----####
####------------------------------------------------------------####
resource "aws_sns_topic" "site_access_alerts" {
  name = "${var.app_name}-site-access-alerts"
}

####------------------------------------------------------------------------####
####----  Assina um e-mail para receber notificações de acesso ao site  ----####
####----  Após o apply, a AWS enviará um e-mail com um link de          ----####
####----  confirmação. É necessário clicar em "Confirm subscription".   ----####
####------------------------------------------------------------------------####
resource "aws_sns_topic_subscription" "email_alert" {
  topic_arn = aws_sns_topic.site_access_alerts.arn
  protocol  = "email"
  endpoint  = "carla_fs@uol.com.br"
}
