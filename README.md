# CRM Produto Digital com AIOX

Sistema completo de CRM para produto digital construido com IA usando AIOX + Claude Code.

## O que este sistema faz

- Gestao de alunos com Kanban board
- Integracao WhatsApp automatica (Evolution API)
- Webhooks de pagamento (Kiwify)
- Recovery automatico de leads abandonados
- CS Agent (Customer Success automatizado)
- Dashboard com metricas em tempo real
- AI Agent para mensagens personalizadas

## Stack

| Tecnologia | Uso |
|-----------|-----|
| Python 3.11+ | Backend |
| FastAPI | Framework web |
| SQLAlchemy Async | ORM |
| PostgreSQL | Banco de dados |
| Evolution API v2 | WhatsApp |
| Kiwify | Pagamentos |
| HTML/CSS/JS | Dashboard |
| Nginx | Reverse proxy |
| DigitalOcean | Hospedagem |
| AIOX + Claude Code | Desenvolvimento com IA |

## Setup Rapido

### 1. Clonar e instalar
```bash
git clone https://github.com/SEU_USUARIO/crm-produto-digital.git
cd crm-produto-digital
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edite o .env com suas credenciais
```

### 2. Instalar AIOX
```bash
npx aiox-core install
```

### 3. Configurar banco de dados
```bash
# Opcao A: DigitalOcean Managed PostgreSQL
# Opcao B: Supabase
# Cole a connection string no .env
```

### 4. Rodar
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Estrutura do Projeto

```
crm-produto-digital/
├── app/
│   ├── main.py              # FastAPI app + scheduler
│   ├── config.py            # Configuracoes (env vars)
│   ├── database.py          # SQLAlchemy async engine
│   ├── models/              # SQLAlchemy models
│   │   ├── customer.py
│   │   ├── order.py
│   │   ├── student.py
│   │   ├── interaction.py
│   │   └── recovery.py
│   ├── routers/             # API endpoints
│   │   ├── health.py
│   │   ├── webhooks.py
│   │   ├── customers.py
│   │   ├── orders.py
│   │   ├── students.py
│   │   ├── recovery.py
│   │   ├── whatsapp.py
│   │   ├── metrics.py
│   │   └── kanban.py
│   ├── services/            # Business logic
│   │   ├── kiwify_processor.py
│   │   ├── evolution_api.py
│   │   ├── cs_agent.py
│   │   ├── auto_recovery.py
│   │   ├── ai_agent.py
│   │   ├── scheduler_service.py
│   │   └── group_whatsapp.py
│   ├── static/              # Frontend
│   │   ├── css/style.css
│   │   └── js/app.js
│   └── templates/
│       └── index.html
├── scripts/
│   ├── setup-server.sh
│   ├── setup-nginx.sh
│   └── deploy.sh
├── docs/
│   └── stories/active/
├── tests/
├── .env.example
├── requirements.txt
├── core-config.yaml
└── README.md
```

## Modulos (ordem de implementacao)

| # | Modulo | Aula |
|---|--------|------|
| 1 | Setup FastAPI + Database | Aula Magna |
| 2 | Models + Migrations | Aula Magna |
| 3 | Webhooks Kiwify | Aula Magna |
| 4 | WhatsApp Evolution API | Aula Magna |
| 5 | Dashboard Frontend | Aula Magna |
| 6 | CS Agent + Recovery | Aula Magna |
| 7 | Deploy DigitalOcean | Aula Magna |

## Comandos AIOX para cada modulo

Ver arquivo `docs/COMANDOS-AIOX.md` para guia completo.

---

*Workshop AIOX Produto Digital | Por Pamela Heimovski*
