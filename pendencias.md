# Pendências

Lista do que falta resolver pra sair do estado atual (motor + relatório + job de
WhatsApp implementados, mas nada rodando em produção com cliente real ainda).
Organizado por quem resolve e o quão bloqueante é.

## Pivot de arquitetura (2026-07-22) — código já migrado, falta ligar de verdade

O `descricao.md` reflete a decisão de ir só com API oficial de plataforma
(Mercado Livre + Shopify + Nuvemshop, em paralelo, tempo real via webhook), e
o backend já tem os três adapters implementados em `app/integrations/`
(`shopify.py`, `mercado_livre.py`, `nuvemshop.py`) + rotas de OAuth/webhook em
`app/api/routes/integrations.py` (ver `CLAUDE.md` pra arquitetura). O que
ainda falta pra isso funcionar com cliente real:

- [ ] **Credenciais reais de app em cada plataforma** — sem
  `SHOPIFY_API_KEY`/`SHOPIFY_API_SECRET`, `MERCADOLIVRE_CLIENT_ID`/`_SECRET`,
  `NUVEMSHOP_CLIENT_ID`/`_SECRET`, `BACKEND_PUBLIC_URL` e
  `INTERNAL_SIGNING_SECRET` configurados, nenhum fluxo de conexão funciona
  (degrada graciosamente: authorize retorna 500 em vez de quebrar).
- [ ] **Verificar contra a documentação atual antes de produção**: o handler
  de Nuvemshop assume que o webhook manda só o id do pedido (precisa buscar
  via API depois) e que a URL de autorização aceita `state` — nenhuma das
  duas suposições foi confirmada contra a doc oficial (ver comentário no
  topo de `app/integrations/nuvemshop.py`).
- [ ] Aplicar/solicitar acesso de parceiro em cada plataforma (Shopify
  Partners, Central de Parceiros do Mercado Livre, programa da Nuvemshop) —
  processo de aprovação externo, prazo fora do nosso controle. Sem isso, o
  OAuth funciona só em modo dev/teste, não pra clientes reais.
- [ ] Registrar os webhooks de pedido em cada plataforma apontando pra
  `/webhooks/{shopify,mercado_livre,nuvemshop}/orders` do backend em produção
  (isso normalmente é feito no painel do parceiro ou via uma chamada de API
  depois do OAuth — não está automatizado ainda).
- [ ] Decidir se `SheetsSource`/`UploadSource` são removidos do código ou só
  deixados pra trás sem uso — `descricao.md` §4 já tira os dois do roadmap
  oficial, mas o código ainda existe (ver nota em `CLAUDE.md`).
- [x] ~~Reescrever a landing page com a mensagem de "tempo real de verdade"~~
  — feito: hero, steps, comparação e preço mencionam as três plataformas, tira
  menção a Sheets/upload. Verificado renderizando no navegador (Playwright),
  sem erro de console. Ainda não testado com login real / dados reais (só a
  rota pública `/`).
- [x] ~~Logo das plataformas no cabeçalho~~ — a pedido explícito do usuário,
  optamos por usar os logos reais **mesmo sem autorização formal ainda**
  (risco assumido conscientemente, já avisado antes de proceder). Assets
  baixados do Wikimedia Commons (`frontend/src/assets/logos/`:
  `mercado-livre.svg`, `shopify.svg`, `nuvemshop.png`) — uso nominativo pra
  identificação, prática padrão, mas ainda não é autorização formal de
  parceiro. Trocar pelos assets oficiais assim que conseguir acesso de
  parceiro em cada plataforma (mesmo item de aprovação já listado acima).
- [x] ~~Refazer ConnectSource.tsx~~ — feito: agora mostra as três plataformas
  (Mercado Livre, Shopify — com campo de domínio da loja —, Nuvemshop), cada
  botão chama `GET /integrations/{platform}/authorize` e redireciona o
  navegador pra `authorize_url` retornada. Testado no navegador com conta
  real + plano ativo simulado direto no banco.
- [ ] Job/endpoint pra fazer o backfill inicial de pedidos históricos ao
  conectar uma conta nova — hoje só ingere pedidos que chegam via webhook
  dali pra frente; nada preenche o antes da conexão.

## Plano e pagamento (2026-07-23) — construído, falta a conta Stripe de verdade

A pedido explícito do usuário: login agora cai numa página de "Seu plano"
(`/plano`) antes de liberar qualquer conexão de dado — só depois do
pagamento confirmado (via webhook do Stripe) o cliente pode conectar
Mercado Livre/Shopify/Nuvemshop. Gateway escolhido: **Stripe** (decisão
explícita do usuário, não Mercado Pago). Testado de ponta a ponta no
navegador simulando os dois estados (`plan_status` pendente e ativo direto
no banco, já que não existe conta Stripe real ainda) — inclusive achei e
corrigi uma race condition real no `App.tsx` nesse processo (ver `CLAUDE.md`
§ Frontend architecture).

- [ ] **Criar produto + price recorrente no Dashboard do Stripe** (R$ 47,00
  mensal, mesmo valor da landing) e colocar `STRIPE_SECRET_KEY` +
  `STRIPE_PRICE_ID` em `backend/.env`. Sem isso, `/billing/checkout` sempre
  responde 500 (degrada graciosamente, não quebra o app).
- [ ] **Configurar o webhook do Stripe** apontando pra
  `/webhooks/stripe` do backend em produção, escutando pelo menos
  `checkout.session.completed`, `customer.subscription.updated` e
  `customer.subscription.deleted`; copiar o signing secret gerado pra
  `STRIPE_WEBHOOK_SECRET`. Sem isso o pagamento nunca ativa a conta de
  verdade (o checkout até abre, mas ninguém nunca vira `plan_status=active`).
- [ ] Testar o fluxo de pagamento de ponta a ponta com uma assinatura real
  (ou o modo de teste do Stripe) — só foi testado simulando o
  `plan_status` direto no banco até agora, nunca um checkout de verdade.
- [ ] Decidir o que acontece quando uma assinatura cai em `past_due` (Stripe
  tenta cobrar de novo e falha) — hoje o webhook só grava o status cru
  vindo do Stripe em `plan_status`, sem nenhum tratamento de UX específico
  pra esse caso (o gate `require_active_plan` só libera `"active"`, então
  na prática já bloqueia, mas a mensagem que o cliente vê é genérica).

## Credenciais e contas externas (só você resolve)

- [ ] **WhatsApp Business API (Meta Cloud API)** — criar app no Meta for
  Developers, gerar `WHATSAPP_API_TOKEN` e `WHATSAPP_PHONE_NUMBER_ID`, colocar
  em `backend/.env`. Sem isso o resumo periódico não sai de verdade (o job só
  loga a falha e segue).
- [x] ~~Supabase (backend)~~ — resolvido. `backend/.env` e `frontend/.env`
  preenchidos com URL/anon/service_role de um projeto real. O projeto usa o
  esquema novo de chave assimétrica (ES256), não o secret HS256 antigo —
  `security.py` foi ajustado pra suportar os dois (ver commit "Fix Supabase
  JWT verification"). Testado de ponta a ponta com conta real (cadastro,
  confirmação de e-mail, login, `/report` autenticado).
- [ ] **Banco de produção** — hoje local é SQLite (`dev.db`); decidir quando
  provisionar o Postgres apontado em `DATABASE_URL`.
- [ ] **Agendador do resumo diário** — nenhum scheduler está rodando ainda.
  Precisa configurar cron / Windows Task Scheduler / scheduler de cloud pra
  chamar `backend/scripts/send_whatsapp_summaries.py` 1x por dia.

## Gaps de produto sem UI/endpoint ainda

- [x] ~~Tela/endpoint pra cadastrar o telefone de WhatsApp~~ — `GET/PATCH /me`
  + página `/configuracoes` no frontend (`Settings.tsx`).
- [x] ~~UI de cadastro de custo/COGS por produto~~ — `GET /products` +
  `PUT /products/{id}/cost`, mesma página `/configuracoes`. Testado via
  pytest (`tests/api/test_clients_route.py`, `tests/api/test_products_route.py`)
  e build do frontend; **não testado em navegador com login real** — o
  backend não tem `SUPABASE_JWT_SECRET` configurado localmente (ver item
  abaixo), então o fluxo autenticado de ponta a ponta ainda depende disso.
- [ ] Sem migrations (Alembic está instalado mas não usado) — mudança de
  schema exige recriar o banco via `scripts/init_db.py`
  (`create_all` não altera tabela existente). Ex: o `whatsapp_phone`
  que acabou de entrar no `Client` não aparece num `dev.db` já existente até
  recriar.

## Decisões de produto em aberto (do `descricao.md`)

- [ ] Contextualização estruturada do negócio no onboarding (formulário
  guiado, não texto livre).
- [ ] Validar com clientes reais se a fricção de cadastrar custo/COGS
  compromete a meta de 10 ativações no mês 1.
- [ ] Validar reação real dos clientes ao pedido de custo por produto nas
  entrevistas.

## Fase 2 (não começar sem validar a Fase 1 primeiro)

- [ ] Pergunta ao vivo via WhatsApp (intents fixas) — pré-requisito de dado já
  fica resolvido pela Fase 1 pivotada; falta só a infra de conversa
  bidirecional (webhook de mensagens recebidas + interpretação de intenção).
- [ ] Expansão de integrações (TikTok Shop, Shopee, Amazon).

## Meta de validação do MVP

- [ ] 10 clientes ativados (conectaram conta + receberam 2+ resumos) no
  primeiro mês — nenhum cliente real ativado ainda.
