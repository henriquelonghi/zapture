# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Product context

Zapture is a SaaS that computes billing/sales insights for e-commerce sellers (Mercado Livre, Shopify, Nuvemshop) and delivers them proactively via WhatsApp, instead of a passive dashboard the seller has to check. Full product spec (target audience, phased scope, metric definitions, architecture rationale) lives in `descricao.md` — read it before making product-shape decisions (which metrics to add, what the WhatsApp summary should contain, onboarding flow, etc).

**Pivot (2026-07-22, see `descricao.md` §1):** the only supported data source going forward is the official platform API (Mercado Livre, Shopify, Nuvemshop in parallel), for real-time-via-webhook data. Sheets/upload are dropped from the roadmap. `SheetsSource`/`UploadSource`/`resync_sheets_if_needed` are the pre-pivot path — still present, not wired to anything new, kept only so existing historical data/tests don't break. The platform integrations are implemented in `app/integrations/` (see below); the frontend `ConnectSource.tsx` and the "escolher método" onboarding flow described further down still reflect the pre-pivot UI and haven't been updated to point at the new OAuth endpoints yet.

Golden rule from the spec: if an LLM is ever used (Fase 2 WhatsApp Q&A), it decides *which question* was asked (intent), never *the answer* (the number). Numbers always come from the deterministic engine described below.

Repo is a monorepo: `backend/` (FastAPI) + `frontend/` (Vite/React), each with its own dependency tree and no shared package.

## GitHub sync

Remote: `https://github.com/henriquelonghi/zapture` (private), branch `main`. After any change to the codebase, commit and push to `origin/main` so the remote stays current — don't let local work sit uncommitted across sessions. Use descriptive commit messages per change (or logical group of changes); don't batch unrelated work into one commit.

## Commands

### Backend (`backend/`)

```bash
# venv already exists at backend/.venv — activate before running anything
.venv\Scripts\Activate.ps1                    # PowerShell
source .venv/Scripts/activate                 # Git Bash

uvicorn app.main:app --reload --port 8000     # dev server, http://localhost:8000/health to check
python scripts/init_db.py                     # create tables in DATABASE_URL (no Alembic migrations wired up yet, just create_all — rerun after model changes)

pytest                                         # full suite (pythonpath=. and testpaths=tests set in pyproject.toml)
pytest tests/engine/test_units.py              # single file
pytest tests/engine/test_units.py::test_units_sold_variation  # single test
```

No `.env` is required for local dev: `Settings` (`app/core/config.py`) defaults `database_url` to `sqlite:///./dev.db`, and every Supabase/Google field is optional (`None`) — features that need them degrade gracefully rather than crashing (see Auth and Ingestion sections below). Copy `.env.example` to `.env` only when you actually need Supabase auth or Google Sheets ingestion to work.

### Frontend (`frontend/`)

```bash
npm run dev        # Vite dev server, http://localhost:5173
npm run build       # tsc -b && vite build
npm run lint         # oxlint
npm run preview
npx tsc --noEmit -p tsconfig.app.json   # type-check only, no lint/build side effects
```

`.env` needs `VITE_SUPABASE_URL` / `VITE_SUPABASE_ANON_KEY` for login to work and `VITE_API_BASE_URL` (defaults to `http://localhost:8000`). Without Supabase configured, `supabaseClient.ts` falls back to a placeholder project and warns in the console — the app still runs, login just won't work.

## Backend architecture

### The engine is one function, two output channels

`app/engine/report_service.py::generate_report(db, client_id, period_start, period_end)` is the single orchestrator: loads normalized `SalesRecord`s for the current period, the equivalent-length previous period, and full history; runs every metric module in `app/engine/metrics/`; builds insight candidates and picks the top 2–3 (`app/engine/insights/rules.py`); returns one `Report` dataclass. This function is meant to be the only thing both the dynamic report endpoint and the (not yet built) WhatsApp summary job call — do not duplicate metric logic elsewhere for a new output channel, extend this function instead.

Metric modules (`app/engine/metrics/*.py`) follow one pattern: a frozen dataclass result + a pure function taking `list[SalesRecord]` (current/previous, sometimes full history), no I/O, no DB session. This is what makes them trivially unit-testable with plain fixtures (see any `tests/engine/test_*.py`). When adding a metric, follow this pattern and wire it into `generate_report` + `Report` dataclass + `ReportOut` (`app/schemas/report.py`) + the matching frontend type in `frontend/src/types/report.ts` (hand-maintained, no codegen — these three have to be updated together or the frontend will silently not see new fields).

Insight scoring (`app/engine/insights/rules.py`) is deliberately explicit and re-calibratable: each metric contributes a candidate insight with a relevance score (variation magnitude, or a fixed base score for categorical alerts — `margem_negativa` = 90, `clientes_sumidos` = 70). `select_top_insights` dedupes by category and always returns between `min_n` (2) and `max_n` (3) when enough candidates exist.

The `/report` endpoint (`app/api/routes/report.py`) recalculates from scratch on every call — that's what "dynamic report" means in this codebase, not that data arrives by itself. If the client's connected source is Google Sheets, `resync_sheets_if_needed` re-fetches before calculating, which is what makes Sheets "live" vs. an upload (which only updates on manual re-upload).

### WhatsApp periodic summary (`app/notifications/`)

The second output channel from the spec's single-engine architecture. `summary_job.py::send_periodic_summaries` is the orchestrator: for every `Client` with `whatsapp_phone` set, it resyncs the source, calls the same `generate_report` the dynamic report uses, formats the result (`summary_formatter.py::format_summary_message`), and sends it (`whatsapp_client.py::send_whatsapp_message`, WhatsApp Cloud API). No metric or insight logic is duplicated here — this module only formats and delivers what the engine already computed.

There's no in-process scheduler yet; `scripts/send_whatsapp_summaries.py` is the entry point meant to be invoked once a day by an external scheduler (cron / Windows Task Scheduler / cloud scheduler), same spirit as `scripts/init_db.py`. Needs `WHATSAPP_API_TOKEN` + `WHATSAPP_PHONE_NUMBER_ID` in `.env` (Meta Cloud API); without them `send_whatsapp_message` just returns `False` per client and the job logs the failure instead of crashing — same graceful-degradation pattern as `supabase_client.py` and Google Sheets ingestion.

The formatted message always ends with the same freshness disclosure the report shows via `LastSyncedBadge` (`dado de: <fonte>, sincronizado em <timestamp>`) — the spec is explicit that "dynamic" means the engine recalculates on open, not that the data itself is live, and the WhatsApp message needs to carry that same caveat since it's pushed proactively rather than opened on demand.

### Ingestion is source-agnostic by design

Any data source implements `IngestionSource.fetch_rows() -> list[dict]` (see `SheetsSource`, `UploadSource`). `app/ingestion/pipeline.py::run_ingestion` is the one path both the upload endpoint and the Sheets resync go through: fetch → `schema_validator.validate_rows` → `normalizer.normalize_and_persist` → update `DataSourceConnection` sync metadata. Adding a new source (e.g. a marketplace API in Fase 2) means implementing `IngestionSource`, not touching the pipeline.

`schema_validator.validate_rows` enforces the "never let a silent error produce a fake number" rule from the spec: missing required columns (`data_pedido`, `pedido_id`, `produto`, `quantidade`, `valor_unitario`) blocks the whole ingestion; missing recommended columns (`sku`, `cliente_id`, `custo_unitario`) becomes a warning and degrades specific features (no `cliente_id` → no churn/new-customer metrics); individual bad rows are excluded one at a time, never zero out or discard the whole batch.

`normalizer.normalize_and_persist` is idempotent per `pedido_id`: re-ingesting the same order replaces its items rather than duplicating them. Product matching is by SKU first, then by name; unit cost resolution order is row-level cost > previously registered `ProductCost` > unavailable (margin metrics handle `None` cost explicitly rather than assuming zero).

### Platform integrations (`app/integrations/`, `app/api/routes/integrations.py`)

One module per marketplace (`shopify.py`, `mercado_livre.py`, `nuvemshop.py`), each exposing the same four functions: `build_authorize_url`, `exchange_code_for_token`, a webhook signature/lookup helper, and `map_order_payload` (platform JSON → the same row-dict shape `schema_validator.validate_rows` already expects: `data_pedido`/`pedido_id`/`produto`/`sku`/`categoria`/`quantidade`/`valor_unitario`/`valor_total`/`cliente_id`/`custo_unitario`). None of them touch the DB directly — routes in `app/api/routes/integrations.py` glue them to `DataSourceConnection` and to `app/ingestion/webhook_pipeline.py::ingest_order_rows`.

`oauth_state.py` signs a short-lived JWT (`internal_signing_secret`, separate from Supabase's) carrying `client_id` + platform name, passed as the OAuth `state` param — the callback is a bare browser redirect from the platform with no bearer token, so this is how we know which client is connecting. `webhook_pipeline.ingest_order_rows` is a copy of `pipeline.run_ingestion` minus the `data_source.config` overwrite: webhook events must never clobber the `config` dict, since that's where the OAuth `access_token` lives for that connection.

Two real asymmetries between platforms, both load-bearing for how the webhook handlers are written:
- **Shopify** sends the full order (line items included) in the webhook payload itself — `map_order_payload` works directly off it. **Mercado Livre and Nuvemshop** webhooks are assumed to only notify "something changed" (an id/resource path); the handler does a follow-up authenticated `fetch_order` call before mapping. This is documented as unverified for Nuvemshop specifically (see inline comment in `nuvemshop.py`) — confirm against current docs before relying on it in production.
- **Cost/COGS never arrives via any of the three APIs in practice** (Mercado Livre has no cost field at all; Shopify/Nuvemshop have one but only if the merchant filled it in on their side) — `custo_unitario` is always `None` from these mappers today. Margin still depends on the manual cost UI that doesn't exist yet (see `pendencias.md`).

Connection lookup for an incoming webhook (`_find_connection_by_config` in the routes module) filters `DataSourceConnection` rows in Python rather than querying into the JSON `config` column — deliberate, to stay portable between Postgres (prod) and SQLite (tests) without DB-specific JSON operators; fine at current expected connection volume, revisit if it ever shows up in profiling.

### Auth and multi-tenancy

There is no backend-native login. The frontend authenticates directly against Supabase (email/password) and sends the JWT as a bearer token. `app/core/security.py::get_current_client` decodes that JWT itself — on a Supabase user's *first* authenticated request, it auto-provisions a `Client` + `ClientMember` workspace keyed by `supabase_user_id`. Every model that holds business data is scoped by `client_id`; there's no cross-tenant query path, so don't add one.

Token verification branches on the JWT's own `alg` header: newer Supabase projects sign with asymmetric keys (ES256/RS256, "JWT Signing Keys") and get verified against Supabase's JWKS endpoint (`PyJWKClient`, cached per-process); anything else falls back to the legacy HS256 shared secret (`SUPABASE_JWT_SECRET`). Both paths pass `leeway=10` to `jwt.decode` — without it, tokens are intermittently rejected as "not yet valid" whenever this machine's clock drifts a couple seconds behind Supabase's auth server.

### Billing (`app/billing/`, `app/api/routes/billing.py`)

One plan (R$ 47/mês, hardcoded in `billing.py::_SINGLE_PLAN` — no plan catalog yet since there's only one), paid via Stripe Checkout in subscription mode. `Client.plan_status` (default `"pending"`) mirrors the Stripe subscription status; `stripe_customer_id`/`stripe_subscription_id` link the two records. `POST /billing/checkout` creates a Checkout Session and returns its URL for the frontend to redirect the browser to; `POST /webhooks/stripe` (signature-verified via `STRIPE_WEBHOOK_SECRET`) is what actually flips `plan_status` to `"active"` on `checkout.session.completed`, and updates/cancels it on `customer.subscription.*` events — the frontend's post-checkout redirect only *polls* for this, it never sets the status itself.

`app/api/deps.py::require_active_plan` gates connecting a data source (the `data-sources` upload/sheets endpoints, the three `/integrations/{platform}/authorize` endpoints) — swap in for `get_current_client` on any new endpoint that lets a client push data in. Viewing the report is deliberately *not* gated (nothing sensitive to protect on an empty report), and neither is `/me` or `/configuracoes` (a client needs to see its own plan status before it's active, and settings aren't a data-connection action).

## Frontend architecture

`App.tsx` gates on two things in sequence: `useSession()` (logged out → `Landing`/`Login` only) then, once authenticated, a `GET /me` fetch to check `plan_status` (logged in but not `"active"` → only `Plano` at `/plano` is reachable, everything else redirects there; `"active"` → `Report`/`ConnectSource`/`Settings`/`Plano` are all reachable). `client` state starts `null` and is reset to `null` at the top of the session-change effect before any fetch — don't reintroduce a separate `clientLoading` boolean here, a past version of this effect had one and it opened a one-render race (`session` truthy, stale `clientLoading=false` from before login, `client` still `null`) that sent freshly-active users back to `/plano` and stuck them there (`/plano` matches an explicit route in both branches, so the catch-all redirect never fires to correct it). `client === null` while a session exists *is* the loading signal — keep it that way.

`Plano.tsx` handles both the "not paid yet" state (plan list + a Stripe Checkout redirect button) and the post-checkout return (`?checkout=sucesso` query param triggers a short `/me` poll loop waiting for the webhook to land, then navigates to `/conectar`; `?checkout=cancelado` just shows a message). `lib/apiClient.ts` attaches the Supabase bearer token to every request automatically.

The marketing landing page and the authenticated dashboard intentionally don't share styling: `landing.css` is imported only by `Landing.tsx` (brand tokens `--brand-navy`/`--brand-gold`, IBM Plex Sans), while `App.css`/`index.css` cover the dashboard (`--accent` purple). Don't merge these — the split keeps the logged-in app's CSS payload from carrying marketing-page styles, and vice versa.
