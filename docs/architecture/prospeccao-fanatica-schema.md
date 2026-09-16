# Camada de Prospecção — baseada em "Prospecção Fanática" (Jeb Blount)

## Origem e decisão

O CRM do workshop nasceu voltado a pós-venda de infoproduto (webhook Kiwify → Customer/Order/Student, recovery de checkout abandonado, CS Agent). O usuário pediu para adicionar uma camada de **pré-venda**: prospecção ativa, modelada sobre os frameworks do livro "Prospecção Fanática" (Jeb Blount).

Decisão registrada em 2026-09-16: **adicionar** a camada de prospecção sem remover o que já existe. `Customer`, `Order`, `Student` e `RecoveryLead` continuam sendo o pós-venda. Esta camada nova (`Lead`, `AtividadeProspeccao`, `MetricaDiaria`) é o pré-venda. Quando um lead fecha negócio, ele passa a referenciar um `Customer` (campo `customer_id`).

O antigo `app/models/interaction.py`, citado no `README.md` e em `app/models/__init__.py` mas nunca implementado, é **substituído** por `AtividadeProspeccao` — que cobre o mesmo papel (registro de toda interação com um lead/cliente) com o vocabulário do livro.

Todo campo abaixo tem origem numa página específica do livro (ver citações). Nada aqui foi inventado sem essa fonte — onde o livro não define uma estrutura de dado (ex: resistência mental, "regra do um a mais"), a informação foi propositalmente deixada de fora do schema.

## Entidades

### `Lead`

Representa um contato em algum ponto da **Pirâmide da Prospecção** (cap. 10, p.121-127) — o funil do livro, que vai da base (contato bruto, dado não verificado) até o ápice (altamente qualificado, janela de compra aberta agora).

| Campo | Tipo | Origem |
|---|---|---|
| `id` | PK | — |
| `nome`, `empresa`, `cargo`, `telefone`, `email` | string | dados básicos de contato |
| `papel_decisor` | enum: `decisor`, `influenciador`, `usuario` | Zona de Ataque, cap.9 p.109-113 |
| `pipeline_stage` | enum: `base_nao_verificado`, `informacao_solida`, `janela_identificada`, `conquista_prioritaria`, `indicacao_quente`, `qualificado_pronto` | Pirâmide da Prospecção, cap.10 p.121-127 (os 6 degraus do livro) |
| `nivel_qualificacao` | enum: `nao_qualificado`, `semiqualificado`, `qualificado_sem_janela`, `qualificado_na_janela` | Zona de Ataque / distribuição gaussiana de qualificação, cap.9 p.109-113 |
| `nivel_familiaridade` | enum: `inativo`, `familiar_na_janela`, `familiar_fora_janela`, `indicacao_quente`, `pouca_familiaridade`, `frio` | Tabela de Contatos por Nível de Familiaridade, cap.9/12 p.117 e p.135 |
| `tentativas_contato` | int, default 0 | mesma tabela acima — define quantas tentativas justificam cada nível (1-3 até 20-50) |
| `territorio`, `origem`, `vertical`, `produto_interesse` | string, nullable | Filtros de Listas Poderosas, cap.10 p.128-129 |
| `sazonal` | bool, default false | idem |
| `nome_guardiao`, `relacionamento_guardiao` | string, nullable | Sete Chaves para Lidar com Guardiões, cap.17 p.248-255 |
| `customer_id` | FK → `customers.id`, nullable | preenchido quando o lead fecha negócio (integração com o módulo pós-venda existente) |
| `created_at`, `updated_at` | datetime | padrão |

### `AtividadeProspeccao`

Um registro por tentativa/contato de prospecção. Substitui `interaction.py`.

| Campo | Tipo | Origem |
|---|---|---|
| `id` | PK | — |
| `lead_id` | FK → `leads.id` | — |
| `canal` | enum: `telefone`, `presencial`, `email`, `venda_social`, `mensagem_texto`, `referencia`, `networking`, `indicacao_interna`, `feira_comercial`, `chamada_fria` | Metodologia Equilibrada de Prospecção, cap.4 p.41-50 |
| `canal_anterior` | enum (mesmo domínio de `canal`), nullable | mede o efeito de sequência de canal — ex: SMS isolado converte 4,8%, SMS após ligação prévia converte 112,6% a mais, cap.20 p.313 |
| `objetivo_contato` | enum: `marcar_reuniao`, `qualificar_informacao`, `fechar_venda`, `construir_familiaridade` | Os Quatro Objetivos da Prospecção, cap.9 p.104-108 |
| `resultado` | enum: `resposta_reflexo`, `dispensa`, `objecao`, `reuniao_marcada`, `venda_fechada`, `sem_resposta` | Taxonomia RDO (Resposta Reflexo / Dispensa / Objeção), cap.16 p.230-245 |
| `motivo_recusa` | enum, nullable: `sem_interesse`, `sem_orcamento`, `ocupado`, `pedido_info`, `sobrecarga`, `so_olhando` | 6 padrões de recusa recorrentes, cap.16 p.230-245 |
| `tecnica_bypass_usada` | enum, nullable: `outro_ramal`, `vendedor_ajuda_vendedor`, `entrada_lateral`, `ligacao_cedo_tarde`, `bilhete_escrito` | Táticas de bypass de guardiões, cap.17 p.248-255 |
| `observacoes` | text, nullable | — |
| `data_hora` | datetime | — |
| `created_at` | datetime | padrão |

### `MetricaDiaria`

Contador diário de atividade, para calcular Eficiência + Eficácia = Desempenho (cap.6, p.61-70). O livro trata isso como algo que o vendedor registra manualmente ("Conheça Seus Números"), não é 100% derivável de `AtividadeProspeccao` porque inclui itens como dados novos coletados que nem sempre viram uma atividade formal.

| Campo | Tipo |
|---|---|
| `id` | PK |
| `data` | date, unique |
| `ligacoes`, `contatos_efetivos`, `emails_enviados`, `respostas`, `reunioes_agendadas`, `vendas_fechadas`, `acoes_sociais`, `mensagens_texto_enviadas`, `novos_dados_coletados` | int, default 0 |
| `created_at`, `updated_at` | datetime |

## Fora de escopo desta camada (não modelar como dado de lead)

- **Resistência mental / gestão de rejeição** (cap.21-22, Loehr, Croner/Abraham, "Regra do Um a Mais"): puramente comportamental/coaching, sem estrutura de dado. Se algum dia virar feature, é um módulo separado de metas pessoais do vendedor — não polui o schema de `Lead`.
- **Templates de roteiro** (5 Passos de telefone/presencial, MUNIÇÃO de e-mail, regras de SMS, cadência de correio de voz): frameworks reais do livro, mas ficam para uma story separada (`TemplateScript`, `TemplateEmail`, `TemplateSms`) — não fazem parte do Módulo 2 (que é o funil em si).
- **Horas de Ouro/Platina e Hub-and-Spoke**: são planejamento de agenda do vendedor, não dado de lead. Candidatos a um módulo futuro de "rotina de prospecção".
- Nenhuma tabela comparativa de taxa de conversão por canal existe no livro (fora do caso pontual SMS-após-telefone) — não inventar uma.

## Fontes

Extraído do PDF `Prospecção Fanática - Jed Blount.pdf` (355 páginas), leitura completa cap.1-23, com página aproximada citada por campo acima.
