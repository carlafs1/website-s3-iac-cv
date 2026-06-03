####----------------------------------------------------------------------------------------####
####----     Verifica existência do bucket efêmero e serve o index.html via proxy S3.   ----####
####----------------------------------------------------------------------------------------####


from botocore.exceptions import ClientError
from aws_clients import s3


# Verifica se bucket efêmero já existe
def bucket_exists(bucket_name):
    try:
        s3.head_bucket(Bucket=bucket_name)
        return True

    except ClientError as erro:
        code = erro.response.get("Error", {}).get("Code")
        print(f"Bucket não acessível ou inexistente: {bucket_name}. Código: {code}")
        return False


# Serve o arquivo index.html
def proxy_s3(bucket_name, event):
    path = event.get("rawPath", "/")
    key = path.lstrip("/") or "index.html"

    print(f"Proxy S3. Bucket: {bucket_name}. Key: {key}")

    try:
        obj = s3.get_object(Bucket=bucket_name, Key=key)

    except ClientError as erro:
        code = erro.response.get("Error", {}).get("Code")

        if code in ("NoSuchKey", "404"):
            print(f"Objeto {key} não encontrado. Tentando index.html.")
            obj = s3.get_object(Bucket=bucket_name, Key="index.html")

        elif code == "NoSuchBucket":
            print(f"Bucket não existe: {bucket_name}")
            raise

        else:
            print(f"Erro inesperado ao buscar objeto S3: {code}")
            raise

    body = obj["Body"].read()
    content_type = obj.get("ContentType", "text/html; charset=utf-8")

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": content_type,
            "Cache-Control": "no-store"
        },
        "body": body.decode("utf-8")
    }
