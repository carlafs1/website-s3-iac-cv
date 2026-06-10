####----------------------------------------------------------------------------------------####
####----                    Módulo de segurança do website efêmero.                     ----####
####----------------------------------------------------------------------------------------####

import json

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

####-------------------------------####
####----  helpers de extração  ----####
####-------------------------------####

def _get_headers(event):
    return event.get("headers") or {}

def _get_user_agent(event):
    return _get_headers(event).get("user-agent", "").lower()

def _get_method(event):
    ctx = event.get("requestContext", {}).get("http", {})
    return ctx.get("method", "GET").upper()

def _get_path(event):
    return event.get("rawPath", "/").lower()

#####--------------------------------####
####----  checagens individuais  ----####
####---------------------------------####
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
    return "accept" not in headers or "accept-language" not in headers

####-----------------------------####
####----  decisão principal  ----####
####-----------------------------####

def is_trusted_access(event):
    """
    Retorna True se o acesso parece humano/legítimo.
    Retorna False se parece scanner ou requisição automatizada.
    Bots permitidos (LinkedIn, Google, etc) passam diretamente.
    Acessos via VPN são aceitos normalmente — a decisão é baseada
    no comportamento da requisição, não na origem do IP.
    Cada rejeição é logada com motivo — útil para dataset futuro.

    Ordem de verificação:
    1. Path suspeito        — rejeita qualquer um, inclusive bots
    2. Método não-GET       — rejeita qualquer um, inclusive bots
    3. Scanner no UA        — rejeita antes de checar bot permitido (anti-spoofing)
    4. Bot permitido        — passa direto, ignora headers de browser
    5. UA ausente           — rejeita
    6. Headers ausentes     — rejeita
    7. Passou tudo          — confiável
    """

    def _reject(reason):
        print(json.dumps({
            "event": "access_decision",
            "trusted": False,
            "reason": reason,
            "user_agent": _get_user_agent(event),
            "path": _get_path(event),
            "method": _get_method(event)
        }))
        return False

    if _is_suspicious_path(event):
        return _reject("suspicious_path")

    if _is_non_get_request(event):
        return _reject("non_get_method")

    if _is_scanner_agent(event):
        return _reject("scanner_agent")

    if _is_allowed_bot(event):
        print(json.dumps({
            "event": "access_decision",
            "trusted": True,
            "reason": "allowed_bot",
            "user_agent": _get_user_agent(event)
        }))
        return True

    if _has_no_user_agent(event):
        return _reject("no_user_agent")

    if _is_missing_browser_headers(event):
        return _reject("missing_browser_headers")

    print(json.dumps({
        "event": "access_decision",
        "trusted": True,
        "reason": "all_checks_passed",
        "user_agent": _get_user_agent(event)
    }))
    return True