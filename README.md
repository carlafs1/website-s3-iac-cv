# Website Efêmero AWS com Terraform

Arquitetura serverless e efêmera para publicação sob demanda de um portfólio estático na AWS.

O projeto provisiona automaticamente a infraestrutura apenas quando alguém acessa o domínio e destrói os recursos após um período configurável de inatividade.

---

# Visão Geral

Este projeto foi criado com foco em:

* redução de custo em ambientes de demonstração;
* automação completa do ciclo de vida;
* infraestrutura como código;
* arquitetura serverless;
* provisionamento sob demanda;
* integração entre AWS, GitHub Actions e Cloudflare.

O fluxo funciona da seguinte forma:

1. O usuário acessa o domínio.
2. A Lambda de controle verifica se o ambiente já existe.
3. Se o ambiente não existir:

   * cria um registro temporário no DynamoDB;
   * dispara o workflow `apply.yml` no GitHub Actions;
   * retorna uma página de espera.
4. O GitHub Actions executa o Terraform e cria:

   * bucket S3;
   * website estático;
   * permissões;
   * infraestrutura necessária.
5. Após criado, os acessos passam a ser servidos diretamente do S3 via proxy.
6. O EventBridge monitora o tempo de inatividade.
7. Após o timeout configurado:

   * o workflow `destroy.yml` é disparado;
   * os recursos efêmeros são destruídos.

---

# Arquitetura

## Componentes AWS

### API Gateway

Recebe os acessos do domínio público.

### Lambda Controle

Responsável por:

* controlar o ciclo de vida;
* decidir quando criar;
* decidir quando destruir;
* atualizar último acesso;
* reagendar o EventBridge;
* disparar workflows do GitHub Actions;
* enviar alertas SNS;
* servir proxy do S3.

### DynamoDB

Armazena:

* bucket ativo;
* timestamps;
* estado temporário de criação.

### EventBridge

Executa verificações automáticas de timeout.

### S3 Website

Hospeda o portfólio estático.

### SNS

Envia alertas de acesso.

### SSM Parameter Store

Controla parâmetros dinâmicos da solução:

* habilitar/desabilitar SNS;
* timeout do ambiente;
* token GitHub;
* repositório GitHub.

### IAM

Gerencia permissões mínimas para:

* Lambda;
* GitHub Actions;
* Terraform;
* S3;
* SSM;
* SNS;
* EventBridge.

---

# Fluxo Completo

## Primeiro acesso

```text
Usuário
   ↓
API Gateway
   ↓
Lambda Controle
   ↓
DynamoDB verifica ambiente
   ↓
Não existe ambiente ativo
   ↓
Cria registro TEMPORARIO
   ↓
Dispara GitHub Actions
   ↓
Terraform Apply
   ↓
Criação do ambiente efêmero
```

---

## Ambiente ativo

```text
Usuário
   ↓
API Gateway
   ↓
Lambda Controle
   ↓
Atualiza last_accessed_at
   ↓
Reagenda EventBridge
   ↓
Proxy para S3
```

---

## Destruição automática

```text
EventBridge
   ↓
Lambda Controle
   ↓
Verifica timeout
   ↓
Sem acesso dentro do período
   ↓
Dispara destroy.yml
   ↓
Terraform Destroy
   ↓
Ambiente removido
```

---

# Estrutura do Projeto

```text
website-s3-iac-cv/
│
├── bootstrap/
│   ├── api_gateway.tf
│   ├── dynamodb.tf
│   ├── eventbridge.tf
│   ├── iam.tf
│   ├── iam_github_actions.tf
│   ├── lambda.tf
│   ├── variables.tf
│   ├── main.tf
│   └── lambda_src/
│       └── controle.py
│
├── efemero/
│   ├── terraform/
│   │   ├── main.tf
│   │   ├── s3.tf
│   │   ├── iam.tf
│   │   ├── lambda.tf
│   │   ├── eventbridge.tf
│   │   └── variables.tf
│   │
│   └── website/
│       └── index.html
│
└── .github/
    └── workflows/
        ├── apply.yml
        └── destroy.yml
```

---

# Tecnologias Utilizadas

## Cloud & Infraestrutura

* AWS Lambda
* API Gateway
* Amazon S3
* DynamoDB
* EventBridge
* SNS
* IAM
* SSM Parameter Store
* Cloudflare

## Infraestrutura como Código

* Terraform

## Automação

* GitHub Actions

## Linguagens

* Python
* HTML
* Terraform HCL

---

# Controle Dinâmico via SSM

## Habilitar ou desabilitar alertas SNS

Parâmetro:

```text
/website-s3-iac-cv/enviar-sms
```

Valores:

```text
true
false
```

---

## Configurar timeout do ambiente

Parâmetro:

```text
/website-s3-iac-cv/site-timeout-minutes
```

Exemplos de timeout:

| Valor | Comportamento         |
| ----- | --------------------- |
| 5     | destrói em 5 minutos  |
| 30    | destrói em 30 minutos |
| 60    | destrói em 1 hora     |
| 720   | destrói em 12 horas   |

---

# Segurança

O projeto utiliza:

* princípio do menor privilégio;
* parâmetros sensíveis no SSM;
* token GitHub criptografado;
* separação entre bootstrap e ambiente efêmero;
* ambiente temporário automaticamente destruído;
* Cloudflare como camada externa.

---

# Diferenciais Técnicos

* ambiente efêmero real;
* custo extremamente reduzido;
* provisionamento sob demanda;
* destruição automática;
* arquitetura serverless;
* integração Terraform + GitHub Actions;
* EventBridge dinâmico;
* parâmetros runtime via SSM;
* sem necessidade de deploy manual.

---

# Como Executar

## Bootstrap inicial

```bash
terraform init
terraform apply
```

---

## Publicar alterações

```bash
git add .
git commit -m "Atualizações"
git push origin main
```

---

# Objetivo do Projeto

Mais do que hospedar um portfólio, este projeto demonstra:

* arquitetura cloud moderna;
* automação ponta a ponta;
* engenharia de infraestrutura;
* governança operacional;
* integração entre serviços AWS;
* visão de custo;
* desenho orientado a eventos;
* maturidade em ambientes críticos.

---

# Autora

## Carla Sampaio

Arquiteta de Soluções e Dados.

Experiência em:

* sistemas críticos;
* engenharia de dados;
* cloud;
* automação;
* infraestrutura como código;
* arquitetura AWS;
* integração e modernização.

LinkedIn:

```text
https://www.linkedin.com/in/carla-fs/
```

GitHub:

```text
https://github.com/carlafs1
```

# Website Efêmero AWS com Terraform

Arquitetura serverless e efêmera para publicação sob demanda de um portfólio estático na AWS.

O projeto provisiona automaticamente a infraestrutura apenas quando alguém acessa o domínio e destrói os recursos após um período configurável de inatividade.

---

# Visão Geral

Este projeto foi criado com foco em:

* redução de custo em ambientes de demonstração;
* automação completa do ciclo de vida;
* infraestrutura como código;
* arquitetura serverless;
* provisionamento sob demanda;
* integração entre AWS, GitHub Actions e Cloudflare.

O fluxo funciona da seguinte forma:

1. O usuário acessa o domínio.
2. A Lambda de controle verifica se o ambiente já existe.
3. Se o ambiente não existir:

   * cria um registro temporário no DynamoDB;
   * dispara o workflow `apply.yml` no GitHub Actions;
   * retorna uma página de espera.
4. O GitHub Actions executa o Terraform e cria:

   * bucket S3;
   * website estático;
   * permissões;
   * infraestrutura necessária.
5. Após criado, os acessos passam a ser servidos diretamente do S3 via proxy.
6. O EventBridge monitora o tempo de inatividade.
7. Após o timeout configurado:

   * o workflow `destroy.yml` é disparado;
   * os recursos efêmeros são destruídos.

---

# Arquitetura

## Componentes AWS

### API Gateway

Recebe os acessos do domínio público.

### Lambda Controle

Responsável por:

* controlar o ciclo de vida;
* decidir quando criar;
* decidir quando destruir;
* atualizar último acesso;
* reagendar o EventBridge;
* disparar workflows do GitHub Actions;
* enviar alertas SNS;
* servir proxy do S3.

### DynamoDB

Armazena:

* bucket ativo;
* timestamps;
* estado temporário de criação.

### EventBridge

Executa verificações automáticas de timeout.

### S3 Website

Hospeda o portfólio estático.

### SNS

Envia alertas de acesso.

### SSM Parameter Store

Controla parâmetros dinâmicos da solução:

* habilitar/desabilitar SNS;
* timeout do ambiente;
* token GitHub;
* repositório GitHub.

### IAM

Gerencia permissões mínimas para:

* Lambda;
* GitHub Actions;
* Terraform;
* S3;
* SSM;
* SNS;
* EventBridge.

---

# Fluxo Completo

## Primeiro acesso

```text
Usuário
   ↓
API Gateway
   ↓
Lambda Controle
   ↓
DynamoDB verifica ambiente
   ↓
Não existe ambiente ativo
   ↓
Cria registro TEMPORARIO
   ↓
Dispara GitHub Actions
   ↓
Terraform Apply
   ↓
Criação do ambiente efêmero
```

---

## Ambiente ativo

```text
Usuário
   ↓
API Gateway
   ↓
Lambda Controle
   ↓
Atualiza last_accessed_at
   ↓
Reagenda EventBridge
   ↓
Proxy para S3
```

---

## Destruição automática

```text
EventBridge
   ↓
Lambda Controle
   ↓
Verifica timeout
   ↓
Sem acesso dentro do período
   ↓
Dispara destroy.yml
   ↓
Terraform Destroy
   ↓
Ambiente removido
```

---

# Estrutura do Projeto

```text
website-s3-iac-cv/
│
├── bootstrap/
│   ├── api_gateway.tf
│   ├── dynamodb.tf
│   ├── eventbridge.tf
│   ├── iam.tf
│   ├── iam_github_actions.tf
│   ├── lambda.tf
│   ├── variables.tf
│   ├── main.tf
│   └── lambda_src/
│       └── controle.py
│
├── efemero/
│   ├── terraform/
│   │   ├── main.tf
│   │   ├── s3.tf
│   │   ├── iam.tf
│   │   ├── lambda.tf
│   │   ├── eventbridge.tf
│   │   └── variables.tf
│   │
│   └── website/
│       └── index.html
│
└── .github/
    └── workflows/
        ├── apply.yml
        └── destroy.yml
```

---

# Tecnologias Utilizadas

## Cloud & Infraestrutura

* AWS Lambda
* API Gateway
* Amazon S3
* DynamoDB
* EventBridge
* SNS
* IAM
* SSM Parameter Store
* Cloudflare

## Infraestrutura como Código

* Terraform

## Automação

* GitHub Actions

## Linguagens

* Python
* HTML
* Terraform HCL

---

# Controle Dinâmico via SSM

## Habilitar ou desabilitar alertas SNS

Parâmetro:

```text
/website-s3-iac-cv/enviar-sms
```

Valores:

```text
true
false
```

---

## Configurar timeout do ambiente

Parâmetro:

```text
/website-s3-iac-cv/site-timeout-minutes
```

Exemplos de timeout:

| Valor | Comportamento         |
| ----- | --------------------- |
| 5     | destrói em 5 minutos  |
| 30    | destrói em 30 minutos |
| 60    | destrói em 1 hora     |
| 720   | destrói em 12 horas   |

---

# Segurança

O projeto utiliza:

* princípio do menor privilégio;
* parâmetros sensíveis no SSM;
* token GitHub criptografado;
* separação entre bootstrap e ambiente efêmero;
* ambiente temporário automaticamente destruído;
* Cloudflare como camada externa.

---

# Diferenciais Técnicos

* ambiente efêmero real;
* custo extremamente reduzido;
* provisionamento sob demanda;
* destruição automática;
* arquitetura serverless;
* integração Terraform + GitHub Actions;
* EventBridge dinâmico;
* parâmetros runtime via SSM;
* sem necessidade de deploy manual.

---

# Como Executar

## Bootstrap inicial

```bash
terraform init
terraform apply
```

---

## Publicar alterações

```bash
git add .
git commit -m "Atualizações"
git push origin main
```

---

# Objetivo do Projeto

Mais do que hospedar um portfólio, este projeto demonstra:

* arquitetura cloud moderna;
* automação ponta a ponta;
* engenharia de infraestrutura;
* governança operacional;
* integração entre serviços AWS;
* visão de custo;
* desenho orientado a eventos;
* maturidade em ambientes críticos.

---

# Autora

## Carla Sampaio

Arquiteta de Soluções e Dados.

Experiência em:

* sistemas críticos;
* engenharia de dados;
* cloud;
* automação;
* infraestrutura como código;
* arquitetura AWS;
* integração e modernização.

LinkedIn:

```text
https://www.linkedin.com/in/carla-fs/
```

GitHub:

```text
https://github.com/carlafs1
```
