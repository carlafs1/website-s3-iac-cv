####----------------------------------------------------------------------------------------####
####----  HTML da página carregada pela APIGateway que informa que o site está em curso ----####
####----------------------------------------------------------------------------------------####

_SHARED_STYLE = """
    :root {
        --bg: #f6f7fa;
        --card-bg: #ffffff;
        --border: #e2e5eb;
        --ink: #1c2430;
        --muted: #6b7380;
        --accent: #2f6fa3;
        --accent-dark: #1f4d73;
        --tag-bg: #eef1f5;
    }

    * { box-sizing: border-box; }

    body {
        margin: 0;
        background: var(--bg);
        color: var(--ink);
        font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        -webkit-font-smoothing: antialiased;
    }

    .topbar {
        max-width: 1080px;
        margin: 0 auto;
        padding: 28px 24px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .wordmark {
        font-family: Georgia, "Times New Roman", serif;
        font-size: 1.15rem;
        letter-spacing: 0.12em;
        color: var(--ink);
    }

    .topbar a {
        font-size: 0.78rem;
        letter-spacing: 0.06em;
        color: var(--muted);
        text-decoration: none;
        font-weight: 500;
    }

    .topbar a:hover { color: var(--accent); }

    hr.rule {
        border: none;
        border-top: 1px solid var(--border);
        max-width: 1080px;
        margin: 0 auto;
    }

    .eyebrow {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        color: var(--accent);
        margin: 0 0 20px;
    }

    .eyebrow .dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: var(--accent);
        display: inline-block;
    }

    h1 {
        font-family: Georgia, "Times New Roman", serif;
        font-weight: 400;
        font-size: 2.6rem;
        line-height: 1.18;
        margin: 0 0 24px;
        color: var(--ink);
    }

    h1 .accent {
        color: var(--accent);
        font-style: italic;
    }

    p.lead {
        font-size: 1rem;
        line-height: 1.7;
        color: #45505f;
        margin: 0 0 32px;
        max-width: 46ch;
    }

    .cta {
        display: inline-block;
        background: var(--accent-dark);
        color: #fff;
        text-decoration: none;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        padding: 15px 26px;
        border-radius: 6px;
        transition: background 0.15s ease;
    }

    .cta:hover { background: #163a57; }
    .cta:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; }

    .card {
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 28px;
        box-shadow: 0 1px 3px rgba(20, 30, 45, 0.04);
    }

    .card-label {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        color: var(--muted);
        margin: 0 0 20px;
    }

    .status-row {
        display: flex;
        align-items: center;
        gap: 14px;
        padding-bottom: 22px;
        margin-bottom: 22px;
        border-bottom: 1px solid var(--border);
    }

    .spinner {
        width: 22px;
        height: 22px;
        min-width: 22px;
        border: 3px solid var(--border);
        border-top: 3px solid var(--accent);
        border-radius: 50%;
        animation: spin 0.9s linear infinite;
    }

    @keyframes spin { to { transform: rotate(360deg); } }

    @media (prefers-reduced-motion: reduce) {
        .spinner { animation: none; }
        .dots span { animation: none !important; opacity: 1 !important; }
    }

    .status-text {
        font-size: 0.92rem;
        font-weight: 600;
        color: var(--ink);
    }

    .dots span {
        opacity: 0;
        animation: blink 1.4s infinite;
    }
    .dots span:nth-child(2) { animation-delay: 0.2s; }
    .dots span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes blink { 0%, 20% { opacity: 0; } 50% { opacity: 1; } 100% { opacity: 0; } }

    .stats-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px 16px;
        margin-bottom: 22px;
    }

    .stat-value {
        font-family: Georgia, "Times New Roman", serif;
        font-size: 1.35rem;
        color: var(--ink);
        line-height: 1.1;
    }

    .stat-label {
        font-size: 0.68rem;
        letter-spacing: 0.05em;
        color: var(--muted);
        margin-top: 4px;
        font-weight: 500;
    }

    .tags {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        padding-top: 20px;
        border-top: 1px solid var(--border);
    }

    .tag {
        font-size: 0.72rem;
        font-weight: 500;
        color: #3a4453;
        background: var(--tag-bg);
        padding: 6px 11px;
        border-radius: 6px;
    }

    footer.note {
        max-width: 1080px;
        margin: 0 auto;
        padding: 0 24px 56px;
        font-size: 0.85rem;
        color: var(--muted);
    }

    footer.note a { color: var(--accent); text-decoration: none; }
    footer.note a:hover { text-decoration: underline; }

    @media (max-width: 760px) {
        main.hero { grid-template-columns: 1fr; padding-top: 40px; }
        h1 { font-size: 2rem; }
    }
"""

_REPO_URL = "https://github.com/carlafs1/website-s3-iac-cv"


def waiting_page():
    print("Retornando página HTML de carregamento.")

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
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portfólio sob demanda</title>
    <style>
        {_SHARED_STYLE}

        main.hero {{
            max-width: 1080px;
            margin: 0 auto;
            padding: 64px 24px 40px;
            display: grid;
            grid-template-columns: 1.15fr 0.85fr;
            gap: 56px;
            align-items: start;
        }}
    </style>
</head>
<body>

    <div class="topbar">
        <div class="wordmark">CARLA SAMPAIO</div>
        <a href="{_REPO_URL}" target="_blank" rel="noopener noreferrer">GITHUB ↗</a>
    </div>
    <hr class="rule">

    <main class="hero">
        <div class="hero-left">
            <p class="eyebrow"><span class="dot"></span> AMBIENTE SENDO PREPARADO</p>
            <h1>O portfólio está<br>sendo <span class="accent">ligado</span>.</h1>
            <p class="lead">
                Este site só existe quando alguém pede para vê-lo. O acesso que você acabou de
                fazer disparou o provisionamento automático da infraestrutura na AWS — o mesmo
                processo descrito na arquitetura deste projeto. Em instantes, o portfólio
                estará no ar.
            </p>
            <a class="cta" href="{_REPO_URL}" target="_blank" rel="noopener noreferrer">
                VER ARQUITETURA NO GITHUB ↗
            </a>
        </div>

        <div class="hero-right">
            <div class="card">
                <p class="card-label">STATUS DO PROVISIONAMENTO</p>
                <div class="status-row">
                    <div class="spinner"></div>
                    <span class="status-text">Provisionando infraestrutura<span class="dots"><span>.</span><span>.</span><span>.</span></span></span>
                </div>
                <div class="stats-grid">
                    <div>
                        <div class="stat-value">~40s</div>
                        <div class="stat-label">SETUP AUTOMÁTICO</div>
                    </div>
                    <div>
                        <div class="stat-value">100%</div>
                        <div class="stat-label">DECLARATIVO (TERRAFORM)</div>
                    </div>
                    <div>
                        <div class="stat-value">Zero</div>
                        <div class="stat-label">CUSTO OCIOSO</div>
                    </div>
                    <div>
                        <div class="stat-value">OIDC</div>
                        <div class="stat-label">AUTENTICAÇÃO AWS</div>
                    </div>
                </div>
                <div class="tags">
                    <span class="tag">AWS Lambda</span>
                    <span class="tag">Terraform</span>
                    <span class="tag">API Gateway</span>
                    <span class="tag">DynamoDB</span>
                    <span class="tag">EventBridge</span>
                    <span class="tag">GitHub Actions</span>
                </div>
            </div>
        </div>
    </main>

    <footer class="note">
        Esta página é atualizada automaticamente a cada 20 segundos. Assim que o ambiente
        estiver pronto, o portfólio será carregado sem nenhuma ação necessária da sua parte.
    </footer>

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
        {_SHARED_STYLE}

        main.hero {{
            max-width: 640px;
            margin: 0 auto;
            padding: 72px 24px 40px;
        }}

        main.hero .card {{ margin-top: 28px; }}
    </style>
</head>
<body>

    <div class="topbar">
        <div class="wordmark">CARLA SAMPAIO</div>
        <a href="{_REPO_URL}" target="_blank" rel="noopener noreferrer">GITHUB ↗</a>
    </div>
    <hr class="rule">

    <main class="hero">
        <p class="eyebrow"><span class="dot"></span> SINCRONIZANDO AMBIENTE</p>
        <h1>Só mais um <span class="accent">instante</span>.</h1>
        <p class="lead">{message}</p>
        <p class="lead" style="margin-bottom: 0;">
            Esta página será atualizada automaticamente em alguns instantes.
        </p>

        <div class="card">
            <p class="card-label">SOBRE ESTA ARQUITETURA</p>
            <p style="font-size: 0.9rem; color: #45505f; line-height: 1.6; margin: 0 0 16px;">
                Este portfólio roda em infraestrutura efêmera: ela é criada sob demanda e
                removida automaticamente após um período sem acessos.
            </p>
            <a class="cta" href="{_REPO_URL}" target="_blank" rel="noopener noreferrer">
                VER ARQUITETURA NO GITHUB ↗
            </a>
        </div>
    </main>

</body>
</html>
"""
    }