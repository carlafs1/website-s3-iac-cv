####------------------------------------------------------------------####
####----          Testes unitários do módulo security.py          ----####
####----   Valida browsers, bots permitidos, scanners e ataques   ----####
####------------------------------------------------------------------####
####----                                                          ----####
####---- - Browsers legítimos                                     ----####
####---- - Bots permitidos                                        ----####
####---- - Bots com path suspeito ou método inválido (spoofing)   ----####
####---- - Bots com scanner no user-agent (spoofing composto)     ----####
####---- - Scanners conhecidos                                    ----####
####---- - Paths suspeitos                                        ----####
####---- - Métodos HTTP inválidos                                 ----####
####---- - Headers obrigatórios                                   ----####
####---- - Casos de borda                                         ----####
####----                                                          ----####
####----   Executado com pytest.                                  ----####
####----                                                          ----####
####------------------------------------------------------------------####

import pytest
from lambda_src.security import is_trusted_access


def _event(
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    path="/",
    method="GET",
    accept="text/html,application/xhtml+xml",
    accept_language="pt-BR,pt;q=0.9",
):
    """Monta um event da Lambda com valores padrão de browser real."""
    headers = {}
    if user_agent:
        headers["user-agent"] = user_agent
    if accept:
        headers["accept"] = accept
    if accept_language:
        headers["accept-language"] = accept_language

    return {
        "headers": headers,
        "rawPath": path,
        "requestContext": {"http": {"method": method}},
    }



####--------------------------------------------------####
####---- Acessos legítimos — devem retornar True  ----####
####--------------------------------------------------####

def test_browser_chrome_passa():
    assert is_trusted_access(_event()) is True


def test_browser_firefox_passa():
    assert is_trusted_access(_event(
        user_agent="Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0"
    )) is True


def test_googlebot_passa():
    assert is_trusted_access(_event(user_agent="Mozilla/5.0 (compatible; Googlebot/2.1)")) is True


def test_bingbot_passa():
    assert is_trusted_access(_event(user_agent="Mozilla/5.0 (compatible; bingbot/2.0)")) is True


def test_github_passa():
    assert is_trusted_access(_event(user_agent="github-camo/1.0")) is True


####-----------------------------------------------------------------####
####----  Bots com spoofing — path suspeito ou método inválido  ----####
####-----------------------------------------------------------------####

def test_googlebot_path_suspeito_rejeitado():
    assert is_trusted_access(_event(
        user_agent="Googlebot/2.1",
        path="/.env"
    )) is False


def test_googlebot_metodo_post_rejeitado():
    assert is_trusted_access(_event(
        user_agent="Googlebot/2.1",
        method="POST"
    )) is False


def test_linkedinbot_path_suspeito_rejeitado():
    assert is_trusted_access(_event(
        user_agent="LinkedInBot/1.0",
        path="/wp-admin"
    )) is False


def test_whatsapp_metodo_delete_rejeitado():
    assert is_trusted_access(_event(
        user_agent="WhatsApp/2.23.1",
        method="DELETE"
    )) is False



####------------------------------------------------------####
####---- Preview Social Media — devem retornar False  ----####
####------------------------------------------------------####
def test_linkedinbot_rejeitado():
    assert is_trusted_access(_event(user_agent="LinkedInBot/1.0")) is False


def test_slackbot_rejeitado():
    assert is_trusted_access(_event(user_agent="Slackbot-LinkExpanding 1.0")) is False


def test_whatsapp_rejeitado():
    assert is_trusted_access(_event(user_agent="WhatsApp/2.23.1")) is False


def test_twitterbot_rejeitado():
    assert is_trusted_access(_event(user_agent="Twitterbot/1.0")) is False


def test_facebookbot_rejeitado():
    assert is_trusted_access(_event(user_agent="facebookexternalhit/1.1")) is False



####------------------------------------------------------------------####
####----  Bots com scanner no user-agent — spoofing composto     ----####
####------------------------------------------------------------------####

def test_bot_permitido_com_scanner_no_user_agent_rejeitado():
    # LinkedInBot composto com zgrab — scanner detectado antes do bot permitido
    assert is_trusted_access(_event(
        user_agent="LinkedInBot/1.0 zgrab/0.x"
    )) is False


def test_googlebot_com_curl_no_user_agent_rejeitado():
    assert is_trusted_access(_event(
        user_agent="Mozilla/5.0 (compatible; Googlebot/2.1) curl/7.88.1"
    )) is False


def test_whatsapp_com_python_requests_no_user_agent_rejeitado():
    assert is_trusted_access(_event(
        user_agent="WhatsApp/2.23.1 python-requests/2.31.0"
    )) is False


####-------------------------------------------------------####
####----  Scanners e automação — devem retornar False  ----####
####-------------------------------------------------------####

def test_sem_user_agent_rejeitado():
    assert is_trusted_access(_event(user_agent="")) is False


def test_shodan_rejeitado():
    assert is_trusted_access(_event(user_agent="shodan.io/1.0")) is False


def test_censys_rejeitado():
    assert is_trusted_access(_event(user_agent="censys/1.0")) is False


def test_nmap_rejeitado():
    assert is_trusted_access(_event(user_agent="nmap scripting engine")) is False


def test_zgrab_rejeitado():
    assert is_trusted_access(_event(user_agent="zgrab/0.x")) is False


def test_masscan_rejeitado():
    assert is_trusted_access(_event(user_agent="masscan/1.3")) is False


def test_curl_rejeitado():
    assert is_trusted_access(_event(user_agent="curl/7.88.1")) is False


def test_wget_rejeitado():
    assert is_trusted_access(_event(user_agent="Wget/1.21.3")) is False


def test_python_requests_rejeitado():
    assert is_trusted_access(_event(user_agent="python-requests/2.31.0")) is False


def test_scrapy_rejeitado():
    assert is_trusted_access(_event(user_agent="Scrapy/2.10.0")) is False


def test_go_http_client_rejeitado():
    assert is_trusted_access(_event(user_agent="Go-http-client/1.1")) is False


def test_l9scan_rejeitado():
    assert is_trusted_access(_event(user_agent="l9scan/2.0")) is False


def test_leakix_rejeitado():
    assert is_trusted_access(_event(user_agent="LeakIX/1.0")) is False


####-------------------------------------------------####
####---  Paths suspeitos — devem retornar False  ----####
####-------------------------------------------------####

def test_path_env_rejeitado():
    assert is_trusted_access(_event(path="/.env")) is False


def test_path_git_rejeitado():
    assert is_trusted_access(_event(path="/.git")) is False


def test_path_wp_admin_rejeitado():
    assert is_trusted_access(_event(path="/wp-admin")) is False


def test_path_wp_login_rejeitado():
    assert is_trusted_access(_event(path="/wp-login")) is False


def test_path_phpmyadmin_rejeitado():
    assert is_trusted_access(_event(path="/phpmyadmin")) is False


def test_path_admin_rejeitado():
    assert is_trusted_access(_event(path="/admin")) is False


def test_path_xmlrpc_rejeitado():
    assert is_trusted_access(_event(path="/xmlrpc.php")) is False


def test_path_shell_rejeitado():
    assert is_trusted_access(_event(path="/shell")) is False


def test_path_config_rejeitado():
    assert is_trusted_access(_event(path="/config")) is False


def test_path_backup_rejeitado():
    assert is_trusted_access(_event(path="/backup")) is False


####---------------------------------------------####
####---  Métodos HTTP — apenas GET é aceito  ----####
####---------------------------------------------####

def test_metodo_post_rejeitado():
    assert is_trusted_access(_event(method="POST")) is False


def test_metodo_put_rejeitado():
    assert is_trusted_access(_event(method="PUT")) is False


def test_metodo_delete_rejeitado():
    assert is_trusted_access(_event(method="DELETE")) is False


def test_metodo_patch_rejeitado():
    assert is_trusted_access(_event(method="PATCH")) is False


def test_metodo_options_rejeitado():
    assert is_trusted_access(_event(method="OPTIONS")) is False



####-------------------------------------------------------------####
####---  Headers de browser ausentes — devem retornar False  ----####
####-------------------------------------------------------------####

def test_sem_accept_rejeitado():
    assert is_trusted_access(_event(accept="")) is False


def test_sem_ambos_headers_rejeitado():
    assert is_trusted_access(_event(accept="", accept_language="")) is False



####---------------------------------------------------------------------------------------####
####---  Headers de browser ausentes - por ora somente language — devem retornar True  ----####
####---------------------------------------------------------------------------------------####

def test_sem_accept_language_passa():
    assert is_trusted_access(_event(accept_language="")) is True    



####--------------------------####
####----  Casos de borda  ----####
####--------------------------####

def test_scanner_embutido_em_ua_composto_rejeitado():
    # zgrab disfarçado dentro de um user-agent que parece browser
    assert is_trusted_access(_event(
        user_agent="Mozilla/5.0 (compatible; zgrab/0.x)"
    )) is False


def test_path_wp_admin_com_subpath_rejeitado():
    assert is_trusted_access(_event(path="/wp-admin/setup-config.php")) is False


def test_path_admin_com_subpath_rejeitado():
    assert is_trusted_access(_event(path="/admin/login")) is False


def test_bot_permitido_ignora_headers_ausentes():
    # bots legítimos não enviam accept-language — devem passar
    assert is_trusted_access(_event(
        user_agent="Googlebot/2.1",
        accept="",
        accept_language=""
    )) is True


def test_headers_case_insensitive_user_agent():
    assert is_trusted_access(_event(user_agent="Shodan.io/1.0")) is False