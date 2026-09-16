# Camada de Prospecção — baseada em "Prospecção Fanática" (Jeb Blount) + aulas Lucas Carmo (Vertex Club)

## Atualização 2026-09-16: aulas Lucas Carmo como segundo pilar

O usuário trouxe 3 transcrições de aulas de vendas (Lucas Carmo, Vertex Club — `01-aula-de-assentamento`, `02-aula-de-fundamentos`, `03-aula-dos-7-passos`) para nortear a prospecção **junto com** o livro, não substituindo-o. As duas fontes descrevem coisas diferentes que coexistem:

- **Pirâmide da Prospecção (livro)** = o quão *qualificado* um lead está (`nivel_qualificacao`, `pipeline_stage`). Isso vira um selo/etiqueta no card do lead, não a coluna do kanban.
- **Funil operacional (aulas)** = em que *fase do processo de contato* o lead está. Confirmado de forma independente nas aulas 1 e 2: são fases deliberadamente separadas, nunca combinadas na mesma ligação. Um aluno chama isso literalmente de "o que vai no CRM". **Esta é a coluna principal do kanban a partir de agora** (decisão do usuário, 2026-09-16).

Funil operacional completo, na ordem (aula 1, confirmado pelo instrutor): **Prospecção → Follow de prospecção → Qualifica/Desqualifica → Assentamento → Reunião de Venda → Negociação → Fechado (Ganho ou Perdido)**.

A aula 3 detalha os **7 Passos** de uma Reunião de Venda (o que acontece *dentro* da etapa "Reunião de Venda" do funil acima):

1. **Apresentação** — reapresentação intencional (mesmo já tendo se apresentado no assentamento), tom de autoridade.
2. **Conexão** (15-20min) — rapport profundo, pergunta com "suposição" (cenário hipotético pra testar crença), identifica perfil comportamental. Regra: falar menos, ouvir mais.
3. **DI — Decisão Imediata** — compromisso verbal do cliente de responder sim/não no final, ANTES do showtime. Script: "posso contar com sua seriedade pelo sim ou pelo não?". Se não topar, não avança pro showtime.
4. **Showtime** (7-10min) — projeto em 3 blocos (visão → pilares → entregáveis), só 1-3 entregáveis mostrados, "menos é mais".
5. **Fechamento** — pré-fechamento ("comprar antes de vender", sim emocional antes do preço) → ancoragem (regra: "cuidado com ancoragem que viaja muito", não comparar com ticket/mercado muito distante) → relembra a DI → abre preço com "regra do silêncio profundo" (fala uma vez, cala, quem fala primeiro perde) e "regra da não-pergunta" (se não perguntar forma de pagamento, não vai fechar) → trata objeção (antecipa/elimina, não "quebra" — mesma filosofia do livro) → celebra.
6. **Referidos** — pega 5-10 indicações NA HORA, ainda na ligação ("referido se pega, não se pede").
7. **Validação** — indicador manda mensagem pré-pronta pro indicado antes do contato frio do vendedor.

Isso **substitui** a genérica "Estrutura de 5 Passos" do livro (item já listado como fora de escopo abaixo).

### Fora de escopo também nas aulas (mesma régua do livro)

Ambição vs. Ganância, gestão emocional/rejeição, SND ("se valoriza, não faz questão, deixa na mão"), fórmula pessoal de proporção (ex: 150 prospecções → 10 ligações → 1 venda, citada como exemplo pessoal do instrutor, não número universal), rotina de 2-3h/dia: tudo mentalidade/coaching do vendedor, mesma categoria do que já ficou fora com o livro (resistência mental). Candidatos a um módulo futuro de "metas pessoais do vendedor", não poluem o schema de `Lead`.

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
| `etapa_processo` | enum: `prospeccao`, `follow_prospeccao`, `qualificado`, `desqualificado`, `assentamento`, `reuniao_venda`, `negociacao`, `fechado_ganho`, `fechado_perdido` | **NOVO — coluna principal do kanban.** Funil operacional, aula 1 (Lucas Carmo), confirmado pelo instrutor como "o que vai no CRM" |
| `decisor_confirmado_presente` | bool, nullable | confirmação explícita, na fase de assentamento, de que o decisor vai estar na reunião de venda — aula 1 |
| `pipeline_stage` | enum: `base_nao_verificado`, `informacao_solida`, `janela_identificada`, `conquista_prioritaria`, `indicacao_quente`, `qualificado_pronto` | Pirâmide da Prospecção, cap.10 p.121-127 (os 6 degraus do livro). **Agora é etiqueta/badge de qualificação no card, não mais a coluna do kanban** (decisão 2026-09-16) |
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
| `objetivo_contato` | enum: `marcar_reuniao`, `qualificar_informacao`, `fechar_venda`, `construir_familiaridade`, `assentamento` | Os Quatro Objetivos da Prospecção, cap.9 p.104-108 (livro) + `assentamento` como 5º valor, aula 1 (Lucas Carmo) |
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

### `ReuniaoVenda`

Uma reunião de fechamento (a etapa `reuniao_venda` do funil operacional, aula 3). Rastreia em qual dos 7 Passos a reunião está/parou.

| Campo | Tipo | Origem |
|---|---|---|
| `id` | PK | — |
| `lead_id` | FK → `leads.id` | — |
| `etapa_atual` | enum: `apresentacao`, `conexao`, `decisao_imediata`, `showtime`, `fechamento`, `referidos`, `validacao` | Os 7 Passos, aula 3 |
| `di_confirmada` | bool, default false | Passo 3 (Decisão Imediata) — compromisso verbal do cliente antes do showtime |
| `di_timestamp` | datetime, nullable | quando a DI foi confirmada |
| `data_hora_inicio` | datetime | — |
| `data_hora_fim` | datetime, nullable | — |
| `resultado` | enum, nullable: `ganho`, `perdido`, `em_andamento` | mapeia pro `fechado_ganho`/`fechado_perdido` de `Lead.etapa_processo` |
| `valor_fechado` | numeric, nullable | preenchido só se `resultado = ganho` |
| `created_at` | datetime | padrão |

### `Referido`

Uma indicação pega ao vivo no Passo 6 (Referidos) de uma `ReuniaoVenda`. "Referido se pega, não se pede" — aula 3.

| Campo | Tipo | Origem |
|---|---|---|
| `id` | PK | — |
| `lead_origem_id` | FK → `leads.id` | o lead que indicou |
| `nome_indicado`, `contato_indicado` | string | — |
| `mensagem_validacao_enviada` | bool, default false | Passo 7 (Validação) — indicador manda mensagem pré-pronta antes do contato frio |
| `data_hora` | datetime | — |
| `created_at` | datetime | padrão |

## Fora de escopo desta camada (não modelar como dado de lead)

- **Resistência mental / gestão de rejeição** (cap.21-22, Loehr, Croner/Abraham, "Regra do Um a Mais"): puramente comportamental/coaching, sem estrutura de dado. Se algum dia virar feature, é um módulo separado de metas pessoais do vendedor — não polui o schema de `Lead`.
- **Templates de roteiro** (MUNIÇÃO de e-mail, regras de SMS, cadência de correio de voz do livro; scripts literais de Apresentação/DI/abertura de preço/pré-fechamento/pedido de referido da aula 3): frameworks e textos reais, mas ficam para uma story separada (`TemplateScript`, `TemplateEmail`, `TemplateSms`) — não fazem parte desta camada de funil. A "Estrutura de 5 Passos" genérica do livro foi substituída pelos 7 Passos da aula 3 (ver acima).
- **Horas de Ouro/Platina e Hub-and-Spoke**: são planejamento de agenda do vendedor, não dado de lead. Candidatos a um módulo futuro de "rotina de prospecção".
- Nenhuma tabela comparativa de taxa de conversão por canal existe no livro (fora do caso pontual SMS-após-telefone) — não inventar uma.

## Fontes

- PDF `Prospecção Fanática - Jed Blount.pdf` (355 páginas), leitura completa cap.1-23, com página aproximada citada por campo acima.
- 3 transcrições de aula, Lucas Carmo (Vertex Club), em `~/Downloads/ocara.ia/o-cara-ia-py/transcricoes/mls/vertex-club/aulas-lucas-carmo/`: `01-aula-de-assentamento-08-04-2026.md`, `02-aula-de-fundamentos-06-04-2026.md`, `03-aula-dos-7-passos-10-04-2026.md`. Leitura completa das 3, com linha aproximada citada por campo acima.
