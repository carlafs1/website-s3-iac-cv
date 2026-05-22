###------------------------------------------------------------------------####
####----  Recurso para gerar um sufixo aleatório para o nome do bucket  ----####
####------------------------------------------------------------------------####
resource "random_id" "bucket_suffix" {
  byte_length = 4
}


####--------------------------------------------------------------------####
####----  Cria o bucket S3 para armazenar os arquivos da aplicação  ----####
####--------------------------------------------------------------------####
resource "aws_s3_bucket" "app_bucket" {
  
  # Nomes de bucket S3 são globalmente únicos
  bucket = "${var.app_name}-efemero-${lower(random_id.bucket_suffix.hex)}"
  tags = {
    Name = "${var.app_name}-bucket"
  }
}


####---------------------------------------------------####
####----  Desabilita o bloqueio de acesso público  ----####   
####---------------------------------------------------####
resource "aws_s3_bucket_public_access_block" "site" {
  bucket = aws_s3_bucket.app_bucket.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}


####----------------------------------------####
#####----  Habilita o website estático  ----####
####----------------------------------------####
resource "aws_s3_bucket_website_configuration" "site" {
  bucket = aws_s3_bucket.app_bucket.id
  index_document {
    suffix = "index.html"
  }
}


####----------------------------------------------------------####
####----  Público — política de leitura para qualquer um  ----####
####----------------------------------------------------------####
resource "aws_s3_bucket_policy" "site" {
  bucket = aws_s3_bucket.app_bucket.id
  depends_on = [
    aws_s3_bucket_public_access_block.site
  ]
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "PublicReadGetObject"
      Effect    = "Allow"
      Principal = "*"
      Action    = "s3:GetObject"
      Resource = "${aws_s3_bucket.app_bucket.arn}/*"
    }]
  })
}


####----------------------------------------------####
####----  Faz o upload do arquivo index.html  ----####
####----------------------------------------------####
resource "aws_s3_object" "index_html" {
  bucket       = aws_s3_bucket.app_bucket.id
  key          = "index.html"
  source       = "../website/index.html"
  content_type = "text/html"
  # Garante que o arquivo seja re-enviado se o conteúdo mudar.
  # Em um site efêmero, optei por não usar etag/filemd5 pois o
  # bucket é destruído e recriado a cada deploy.
}


####----------------------------------------------####
####----  Exporta a URL do website estático  ----####
####----------------------------------------------####
output "website_url" {
  value = "http://${aws_s3_bucket_website_configuration.site.website_endpoint}"
}