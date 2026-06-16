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
    "/config",
    "/backup",
]
def _get_headers(event):
    headers = event.get("headers") or {}
    return {str(k).lower(): str(v) for k, v in headers.items() if v is not None}
def _get_user_agent(headers):
    return headers.get("user-agent", "").lower()
def _get_path(event):
    return (
        event.get("rawPath")
        or event.get("path")
        or event.get("requestContext", {}).get("http", {}).get("path")
        or ""
    ).lower()
def _log_security_decision(decision, reason, details=None):
    payload = {
        "security_decision": decision,
        "reason": reason,
    }
    if details:
        payload.update(details)
    print(json.dumps(payload, ensure_ascii=False))
def is_trusted_access(event):
    headers = _get_headers(event)
    user_agent = _get_user_agent(headers)
    path = _get_path(event)
    accept_language = headers.get("accept-language", "")
    for suspicious_path in SUSPICIOUS_PATHS:
        if path.startswith(suspicious_path):
            _log_security_decision(
                False,
                "suspicious_path",
                {
                    "path": path,
                    "matched_path": suspicious_path,
                    "user_agent": user_agent,
                },
            )
            return False
    for scanner in SCANNER_USER_AGENTS:
        if scanner in user_agent:
            _log_security_decision(
                False,
                "scanner_user_agent",
                {
                    "matched_user_agent": scanner,
                    "user_agent": user_agent,
                    "path": path,
                },
            )
            return False
    for social_bot in SOCIAL_PREVIEW_BOTS:
        if social_bot in user_agent:
            _log_security_decision(
                False,
                "social_preview_bot",
                {
                    "matched_user_agent": social_bot,
                    "user_agent": user_agent,
                    "path": path,
                },
            )
            return False
    for allowed_bot in ALLOWED_BOTS:
        if allowed_bot in user_agent:
            _log_security_decision(
                True,
                "allowed_search_bot",
                {
                    "matched_user_agent": allowed_bot,
                    "user_agent": user_agent,
                    "path": path,
                },
            )
            return True
    if not accept_language:
        _log_security_decision(
            True,
            "missing_accept_language_allowed",
            {
                "user_agent": user_agent,
                "path": path,
            },
        )
        return True
    _log_security_decision(
        True,
        "trusted_human_access",
        {
            "user_agent": user_agent,
            "path": path,
            "accept_language": accept_language,
        },
    )
    return True
    