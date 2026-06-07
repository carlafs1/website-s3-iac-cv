####----------------------------------------------------------------------------------------####
####----  HTML da página carregada pela APIGateway que informa que o site está em curso ----####
####----------------------------------------------------------------------------------------####

def waiting_page():
    print("Retornando página HTML de carregamento.")

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "text/html; charset=utf-8",
            "Cache-Control": "no-store"
        },
        "body": """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="20">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portfólio sob demanda</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 760px;
            margin: 80px auto;
            padding: 0 24px;
            line-height: 1.6;
            color: #333;
        }

        h1 {
            color: #111;
            margin-bottom: 24px;
        }

        .spinner {
            width: 32px;
            height: 32px;
            border: 4px solid #e5e5e5;
            border-top: 4px solid #333;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 30px 0;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        a {
            color: #0a66c2;
            text-decoration: none;
        }

        a:hover {
            text-decoration: underline;
        }

        .note {
            margin-top: 32px;
            font-size: 0.95rem;
            color: #666;
        }
    </style>
</head>
<body>
    <h1>Preparando o portfólio</h1>

    <p>
        Este site é disponibilizado sob demanda.
    </p>

    <p>
        O ambiente deste portfólio está sendo iniciado automaticamente na AWS.
        Esse processo pode levar alguns instantes.
    </p>

    <p>
        Assim que a infraestrutura estiver pronta, esta página será atualizada
        automaticamente.
    </p>

    <div class="spinner"></div>

    <p class="note">
        Se quiser entender a arquitetura por trás desta solução,
        a explicação completa está no
        <a
            href="https://github.com/carlafs1/website-s3-iac-cv"
            target="_blank"
            rel="noopener noreferrer"
        >
            README do projeto
        </a>.
    </p>
</body>
</html>
"""
    }


def scanner_ignored_page():
# Retorna a mesma página de espera intencionalmente — o scanner não deve saber que foi identificado e bloqueado.
    print("Acesso não confiável. Retornando página neutra sem acordar o ambiente.")
    return waiting_page()


def error_page(message="Não foi possível carregar o portfólio neste momento."):
# statusCode 200 intencional: evita página de erro padrão do browser.
# O conteúdo já informa o usuário e faz refresh automático.    
    print(f"Retornando página de erro: {message}")

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "text/html; charset=utf-8",
            "Cache-Control": "no-store"
        },
        "body": f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="20">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portfólio sob demanda</title>

    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 760px;
            margin: 80px auto;
            padding: 0 24px;
            line-height: 1.6;
            color: #333;
        }}

        h1 {{
            color: #111;
            margin-bottom: 24px;
        }}

        a {{
            color: #0a66c2;
            text-decoration: none;
        }}

        a:hover {{
            text-decoration: underline;
        }}

        .note {{
            margin-top: 32px;
            font-size: 0.95rem;
            color: #666;
        }}
    </style>
</head>
<body>
    <h1>Portfólio temporariamente indisponível</h1>

    <p>{message}</p>

    <p>
        Esta página será atualizada automaticamente em alguns instantes.
    </p>

    <p class="note">
        A arquitetura do projeto está documentada no
        <a
            href="https://github.com/carlafs1/website-s3-iac-cv"
            target="_blank"
            rel="noopener noreferrer"
        >
            README do projeto
        </a>.
    </p>
</body>
</html>
"""
    }
