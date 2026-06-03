####----------------------------------------------------------------------------------------####
####----                    Módulo de segurança do website efêmero.                     ----####
####----------------------------------------------------------------------------------------####

SCANNER_USER_AGENTS = [
    "l9scan",
    "leakix",
    "censys",
    "shodan",
    "zgrab",
    "masscan",
    "nmap",
    "python-requests",
    "scrapy",
    "go-http-client",
    "curl",
    "wget",
]

ALLOWED_BOTS = [
    "linkedinbot",
    "github",
    "googlebot",
    "bingbot",
    "facebookexternalhit",
    "twitterbot",
    "slackbot",
    "whatsapp",
]

SUSPICIOUS_PATHS = [
    "/.env",
    "/.git",
    "/wp-admin",
    "/wp-login",
    "/phpmyadmin",
    "/admin",
    "/xmlrpc.php",
    "/shell",
    "/config",
    "/backup",
]

####----
####----  helpers de extração - extrair uma informação específica do objeto event
####----
def _get_headers(event):
    return event.get("headers") or {}


def _get_user_agent(event):
    return _get_headers(event).get("user-agent", "").lower()


def _get_method(event):
    ctx = event.get("requestContext", {}).get("http", {})
    return ctx.get("method", "GET").upper()


def _get_path(event):
    return event.get("rawPath", "/").lower()



####----
####---  checagens individuais - classifica o tipo de acesso
####----
def _has_no_user_agent(event):
    return not _get_user_agent(event)


def _is_scanner_agent(event):
    ua = _get_user_agent(event)
    return any(s in ua for s in SCANNER_USER_AGENTS)


def _is_allowed_bot(event):
    ua = _get_user_agent(event)
    return any(b in ua for b in ALLOWED_BOTS)


def _is_suspicious_path(event):
    path = _get_path(event)
    return any(path.startswith(p) for p in SUSPICIOUS_PATHS)


def _is_non_get_request(event):
    return _get_method(event) != "GET"


def _is_missing_browser_headers(event):
    headers = _get_headers(event)
    has_accept = "accept" in headers
    has_language = "accept-language" in headers
    return not has_accept or not has_language



####----
####----  decisão principal  
####----
def is_trusted_access(event):
    """
    Retorna True se o acesso parece humano/legítimo.
    Retorna False se parece scanner ou requisição automatizada.

    Bots permitidos (LinkedIn, Google, etc) passam diretamente.
    Acessos via VPN são aceitos normalmente — a decisão é baseada
    no comportamento da requisição, não na origem do IP.

    Cada rejeição é logada com motivo — útil para dataset futuro.
    """

    if _is_allowed_bot(event):
        print("Acesso confiável: bot permitido.")
        return True

    if _has_no_user_agent(event):
        print("Acesso rejeitado: user-agent ausente.")
        return False

    if _is_scanner_agent(event):
        print(f"Acesso rejeitado: user-agent de scanner ({_get_user_agent(event)}).")
        return False

    if _is_suspicious_path(event):
        print(f"Acesso rejeitado: path suspeito ({_get_path(event)}).")
        return False

    if _is_non_get_request(event):
        print(f"Acesso rejeitado: método não-GET ({_get_method(event)}).")
        return False

    if _is_missing_browser_headers(event):
        print("Acesso rejeitado: headers básicos de browser ausentes (accept / accept-language).")
        return False

    print("Acesso confiável: passou todas as verificações.")
    return True
