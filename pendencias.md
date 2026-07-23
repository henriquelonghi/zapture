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
- [ ] Resolver uso de marca/logo por plataforma antes de colocar qualquer logo
  na landing — Shopify tem brand kit público com regras estritas; Mercado
  Livre exige autorização por escrito; Nuvemshop ainda não verificado. Usar
  nome em texto até resolver oficialmente.
- [ ] Reescrever a landing page com a mensagem de "tempo real de verdade" —
  agora que a integração existe no backend, dá pra fazer isso sem prometer o
  que não existe.
- [ ] Refazer `ConnectSource.tsx`: hoje ainda mostra a tela de "escolher
  método de importação" (Sheets/upload); precisa virar "escolher plataforma"
  chamando `GET /integrations/{platform}/authorize` e redirecionando o
  navegador pra `authorize_url` retornada.
- [ ] Job/endpoint pra fazer o backfill inicial de pedidos históricos ao
  conectar uma conta nova — hoje só ingere pedidos que chegam via webhook
  dali pra frente; nada preenche o antes da conexão.

## Credenciais e contas externas (só você resolve)

- [ ] **WhatsApp Business API (Meta Cloud API)** — criar app no Meta for
  Developers, gerar `WHATSAPP_API_TOKEN` e `WHATSAPP_PHONE_NUMBER_ID`, colocar
  em `backend/.env`. Sem isso o resumo periódico não sai de verdade (o job só
  loga a falha e segue).
- [ ] **Supabase (backend)** — `frontend/.env` já tem `VITE_SUPABASE_URL` e
  `VITE_SUPABASE_ANON_KEY`; falta confirmar se `backend/.env` tem
  `SUPABASE_JWT_SECRET` (obrigatório pra validar login) e
  `SUPABASE_SERVICE_ROLE_KEY` (usado pro Storage do upload original).
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
