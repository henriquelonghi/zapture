# Pendências

Lista do que falta resolver pra sair do estado atual (motor + relatório + job de
WhatsApp implementados, mas nada rodando em produção com cliente real ainda).
Organizado por quem resolve e o quão bloqueante é.

## Credenciais e contas externas (só você resolve)

- [ ] **WhatsApp Business API (Meta Cloud API)** — criar app no Meta for
  Developers, gerar `WHATSAPP_API_TOKEN` e `WHATSAPP_PHONE_NUMBER_ID`, colocar
  em `backend/.env`. Sem isso o resumo periódico não sai de verdade (o job só
  loga a falha e segue).
- [ ] **Supabase (backend)** — `frontend/.env` já tem `VITE_SUPABASE_URL` e
  `VITE_SUPABASE_ANON_KEY`; falta confirmar se `backend/.env` tem
  `SUPABASE_JWT_SECRET` (obrigatório pra validar login) e
  `SUPABASE_SERVICE_ROLE_KEY` (usado pro Storage do upload original).
- [ ] **Service account do Google (Sheets)** — `GOOGLE_SERVICE_ACCOUNT_JSON`
  ainda não configurado; sem isso, conectar planilha falha com erro 500.
- [ ] **Banco de produção** — hoje local é SQLite (`dev.db`); decidir quando
  provisionar o Postgres apontado em `DATABASE_URL`.
- [ ] **Agendador do resumo diário** — nenhum scheduler está rodando ainda.
  Precisa configurar cron / Windows Task Scheduler / scheduler de cloud pra
  chamar `backend/scripts/send_whatsapp_summaries.py` 1x por dia.

## Gaps de produto sem UI/endpoint ainda

- [ ] Não existe tela nem endpoint pra o cliente cadastrar o próprio número de
  WhatsApp — `Client.whatsapp_phone` só existe no banco por enquanto.
- [ ] Não existe UI de cadastro de custo/COGS por produto (sem isso, margem
  fica sempre indisponível). Citado no `descricao.md` (seção 6) como algo "a
  decidir/desenhar em seguida" — ainda não desenhado.
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

- [ ] Pergunta ao vivo via WhatsApp (intents fixas) — requer fonte via API de
  plataforma, Sheets/upload não sustentam isso de forma confiável.
- [ ] Integração com API de marketplace (Mercado Livre / Shopify /
  Nuvemshop) — hoje só existem Sheets e upload.
- [ ] Expansão de integrações (TikTok Shop, Shopee, Amazon).

## Meta de validação do MVP

- [ ] 10 clientes ativados (conectaram conta + receberam 2+ resumos) no
  primeiro mês — nenhum cliente real ativado ainda.
