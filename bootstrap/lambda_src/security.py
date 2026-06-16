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

SOCIAL_PREVIEW_BOTS = [
    "linkedinbot",
    "facebookexternalhit",
    "facebot",
    "twitterbot",
    "slackbot",
    "whatsapp",
    "discordbot",
]

ALLOWED_BOTS = [
    "googlebot",
    "bingbot",
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

def _is_social_preview_bot(event):
    ua = _get_user_agent(event)
    return any(b in ua for b in SOCIAL_PREVIEW_BOTS)

def _is_allowed_bot(event):
    ua = _get_user_agent(event)
    return any(b in ua for b in ALLOWED_BOTS)

def _is_suspicious_path(event):
    path = _get_path(event)
    return any(path.startswith(p) for p in SUSPICIOUS_PATHS)

def _is_non_get_request(event):
    return _get_method(event) != "GET"

def _is_missing_accept_header(event):
    headers = _get_headers(event)
    return "accept" not in headers

def _is_missing_accept_language(event):
    headers = _get_headers(event)
    return "accept-language" not in headers

####-----------------------------####
####----  decisão principal  ----####
####-----------------------------####

def is_trusted_access(event):
    """
    Retorna True se o acesso parece humano/legítimo.
    Retorna False se parece scanner, preview social ou requisição automatizada.

    Bots de busca permitidos passam diretamente.
    Previews sociais são bloqueados para não acordar o ambiente.
    Acessos sem accept-language são permitidos para evitar falso bloqueio
    de humanos, VPNs, proxies corporativos ou navegadores intermediados.

    Acessos via VPN são aceitos normalmente — a decisão é baseada
    no comportamento da requisição, não na origem do IP.

    Cada rejeição ou permissão relevante é logada com motivo — útil para dataset futuro.

    Ordem de verificação:
    1. Path suspeito              — rejeita qualquer um, inclusive bots.
    2. Método não-GET             — rejeita qualquer um, inclusive bots.
    3. Scanner no UA              — rejeita antes de checar bot permitido.
    4. Preview social             — rejeita sem provisionar ambiente.
    5. Bot de busca permitido     — passa direto.
    6. UA ausente                 — rejeita.
    7. Header accept ausente      — rejeita.
    8. Accept-language ausente    — permite, mas loga motivo específico.
    9. Passou tudo                — confiável.
    """

    def _decision(trusted, reason):
        print(json.dumps({
            "event": "access_decision",
            "trusted": trusted,
            "reason": reason,
            "user_agent": _get_user_agent(event),
            "path": _get_path(event),
            "method": _get_method(event)
        }))
        return trusted

    if _is_suspicious_path(event):
        return _decision(False, "suspicious_path")

    if _is_non_get_request(event):
        return _decision(False, "non_get_method")

    if _is_scanner_agent(event):
        return _decision(False, "scanner_agent")

    if _is_social_preview_bot(event):
        return _decision(False, "social_preview_bot")

    if _is_allowed_bot(event):
        return _decision(True, "allowed_search_bot")

    if _has_no_user_agent(event):
        return _decision(False, "no_user_agent")

    if _is_missing_accept_header(event):
        return _decision(False, "missing_accept_header")

    if _is_missing_accept_language(event):
        return _decision(True, "missing_accept_language_allowed")

    return _decision(True, "all_checks_passed")