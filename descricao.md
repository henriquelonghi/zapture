# Especificação do MVP — SaaS de Relatórios e Insights de Faturamento

## 1. Contexto do produto

**Público-alvo (nicho de validação inicial):** sellers de e-commerce que vendem em marketplaces (Mercado Livre, Shopify, Nuvemshop), com foco em volume de aquisição via comunidades (Telegram/Facebook/WhatsApp de sellers).

**Proposta de valor central:**
> "Enquanto ferramentas tradicionais te dão um painel completo pra consultar, a gente te manda o que importa direto no WhatsApp, sem você precisar ir atrás."

**Diferencial frente à concorrência (ex: SellerHub Analytics, Nubimetrics):** entrega proativa via WhatsApp como canal principal, não só dashboard passivo. Preço público e simples.

**Decisão de pivot (2026-07-22):** dado real, ao vivo, é mais interessante como produto do que dado "tão vivo quanto a última atualização manual do cliente". A partir desta versão, a única fonte de dado suportada é a **API oficial da plataforma** (Mercado Livre, Shopify, Nuvemshop, integradas em paralelo desde o MVP) — Sheets e upload de CSV/XLSX saem do roadmap. Isso é assumido conscientemente: sacrifica o seller que só quer subir uma planilha sem conectar a conta oficial, mas troca isso por métricas genuinamente em tempo real via webhook em vez de recálculo sobre dado potencialmente parado.

**Meta de validação:** 10 clientes ativados (conectaram conta via API oficial de uma das três plataformas + receberam ao menos 2 resumos) no primeiro mês.

---

## 2. Escopo por fases

### Fase 1 — MVP
1. Landing page (aquisição/conversão) — mensagem central agora é "tempo real de verdade", não mais "não precisa ir atrás"
2. Integração via API oficial com Mercado Livre, Shopify e Nuvemshop em paralelo (OAuth + webhook de pedidos por plataforma — ver seção 4)
3. Motor de dados (ingestão + validação + cálculo de métricas + priorização de insights) — mesma lógica de antes, agora alimentado só por webhook
4. Relatório **dinâmico** (calcula na hora que é aberto; com API + webhook, o dado subjacente também já chega sozinho, não só o cálculo)
5. Resumo periódico automático via WhatsApp

### Fase 2 — pós-validação
1. Pergunta ao vivo via WhatsApp (conjunto **fixo** de intenções, não NLU aberto):
   - "Qual foi o produto mais vendido até agora no mês?"
   - "Quantos de [produto] foram vendidos?"
   - "Qual o faturamento de hoje?"
2. Pré-requisito de dado (fonte via API) já fica resolvido na Fase 1 com o pivot — o que falta pra Fase 2 é só a infraestrutura de conversa bidirecional (webhook de mensagens recebidas + interpretação de intenção), não mais a fonte de dado
3. Expansão de integrações (TikTok Shop, Shopee, Amazon, etc.)

**Regra de ouro entre fases:** o LLM (se usado) decide *qual pergunta é essa* (intenção), nunca *qual é a resposta* (o número). O número sempre vem do motor determinístico.

---

## 3. Métricas do motor (Fase 1)

**Camada financeira**
- Faturamento total do período + variação % vs. período anterior
- Margem/lucro por produto (requer custo/COGS cadastrado pelo cliente) + margem agregada do período — **o pivot pra API não resolve isso**: Mercado Livre não tem campo de custo na API (nunca vai ter, é só marketplace); Shopify e Nuvemshop têm o campo (`cost` do inventário/variante), mas só populado se o próprio lojista preencheu do lado de lá. Cadastro manual de custo dentro do nosso produto continua necessário nos três casos na prática.
- Ticket médio + variação

**Camada de produto/categoria**
- Ranking de categorias/produtos por variação (subiu/caiu)
- Produtos com margem negativa (alerta prioritário — gancho de venda validado na concorrência)

**Camada de cliente**
- Clientes que sumiram (sem compra há X dias, comparado ao padrão histórico dele)

**Camada de volume**
- Número de pedidos + variação

O motor de regras de insight seleciona os **2-3 mais relevantes** desses cálculos pra compor o resumo do WhatsApp (não despeja a lista inteira).

---

## 4. Fontes de dado e suas capacidades

Única fonte suportada a partir deste pivot: **API oficial da plataforma**, uma integração por marketplace, todas ativas desde o MVP. Sheets e upload de CSV/XLSX saem do roadmap (ver seção 7 pra risco/trade-off assumido).

| Plataforma | Atualização | Webhook de pedidos | Margem por produto (campo de custo nativo) | Uso de marca/logo |
|---|---|---|---|---|
| Mercado Livre | Tempo real | `orders_v2` | Não existe — sempre manual | Requer autorização por escrito (sem brand kit público) |
| Shopify | Tempo real | `orders/create`, `orders/updated`, `orders/paid` | Sim, `InventoryItem.cost` — só se o lojista preencheu no admin dele | Partner Toolkit público, uso monocromático, regras estritas |
| Nuvemshop | Tempo real | `order/created`, `order/paid`, `order/updated` | Sim, `cost` da variante — mesma ressalva de preenchimento | Verificar programa de parceiros deles antes de usar logo |

**Decisões de arquitetura:**
- Cada plataforma exige seu próprio fluxo OAuth (app instalável na loja/conta do seller) + endpoint de webhook próprio, com validação de assinatura e idempotência por `order_id` — infraestrutura crítica desde o dia 1, não mais um item de Fase 2.
- "Dinâmico" continua significando que o motor recalcula a cada abertura do relatório — a diferença é que agora o dado subjacente também chega sozinho via webhook, então recalcular sobre dado parado deixa de ser um cenário esperado (só acontece se o webhook falhar).
- Mostrar timestamp de última atualização de forma persistente e discreta dentro do relatório (ex: "dado de: Mercado Livre, sincronizado em [data/hora]") — vale mesmo com webhook, como sinal de saúde da integração pro cliente perceber se algo parou de sincronizar.
- Validar estrutura esperada no momento da ingestão (schema check) e avisar o cliente se um webhook chegar com payload inesperado — nunca deixar erro silencioso gerar número furado.

---

## 5. Arquitetura geral (alto nível)

```
[Mercado Livre API] ─┐
[Shopify API]       ─┼─(OAuth + webhook de pedidos)─► [Motor de dados: valida + calcula métricas + prioriza insights] ─┬─► [Relatório dinâmico]
[Nuvemshop API]      ─┘                                                                                                 └─► [Resumo WhatsApp periódico]
```

- Um único motor de cálculo alimenta os dois canais de saída — não há duplicação de lógica entre relatório e resumo.
- Cada plataforma tem seu próprio adapter de ingestão (mesmo padrão de fonte-agnóstica já usado no código: implementar a interface de ingestão, não tocar no pipeline), mas todos convergem pro mesmo motor.
- Fase 2 adiciona um interpretador de intenção antes do motor, para o fluxo de pergunta-resposta via WhatsApp (fluxo bidirecional, requer webhook + conta WhatsApp Business API) — a única coisa nova em Fase 2 é essa infra de conversa, já que a fonte de dado via API deixou de ser um pré-requisito exclusivo dela.

---

## 6. Onboarding — pontos a decidir/desenhar em seguida

- Contextualização estruturada do negócio (formulário, não texto livre) para calibrar o motor de regras.
- Escolha da plataforma pra conectar (Mercado Livre / Shopify / Nuvemshop), cada uma abrindo o fluxo OAuth oficial dela — troca a antiga tela de "escolher método de importação" por "autorizar acesso à sua conta". Sem mapeamento de coluna de planilha pra desenhar (isso já não existe mais).
- Cadastro de custo/COGS por produto (fricção conhecida e aceita conscientemente — validar reação real do cliente nas entrevistas). Esse ponto não muda com o pivot: nenhuma das três plataformas resolve isso de graça pra Mercado Livre, e mesmo Shopify/Nuvemshop dependem do lojista já ter preenchido o campo do lado de lá.
- Cada plataforma provavelmente exige processo de aprovação de app antes de liberar OAuth pra qualquer cliente real (Shopify App Store review, aplicação de parceiro no Mercado Livre, etc.) — isso é trabalho de onboarding "nosso", não do cliente, mas bloqueia o lançamento até estar aprovado.

---

## 7. Riscos e trade-offs assumidos conscientemente

- Margem completa por produto aumenta fricção de ativação — decisão tomada de forma consciente, validar com clientes reais se a fricção compromete a meta de 10 ativações no mês 1. Continua valendo com o pivot pra API.
- **Sacrifício de público assumido conscientemente:** derrubar Sheets/upload do roadmap significa que qualquer seller que não conecta a conta oficial via API (por não confiar, por não ter permissão de admin da loja, por vender em plataforma não suportada, etc.) fica de fora do MVP. Aceito em troca de dado genuinamente em tempo real em vez de "tão vivo quanto a última atualização manual".
- **Escopo de engenharia do MVP cresce**: em vez de uma integração leve (Sheets/upload) pra validar rápido, o MVP agora exige três integrações OAuth + webhook completas (Mercado Livre, Shopify, Nuvemshop) antes de conseguir ativar o primeiro cliente em qualquer uma delas — mais tempo até o primeiro lançamento.
- **Aprovação externa vira bloqueador de lançamento**: cada marketplace pode exigir review/aprovação de app antes de liberar OAuth pra clientes reais — esse prazo não está sob nosso controle.
- **Webhook como infraestrutura crítica desde o dia 1**: confiabilidade de entrega (retry, replay, idempotência, validação de assinatura) deixa de ser um problema "de Fase 2" e vira responsabilidade do MVP.
- **Uso de marca/logo das plataformas** segue regras distintas e não triviais por parceiro — Shopify tem brand kit público com regras estritas; Mercado Livre exige autorização por escrito e não tem um kit de marca aberto equivalente; Nuvemshop precisa ser verificado. Até resolver isso oficialmente, usar nome em texto em vez do logo é o caminho mais seguro pra landing e app.
- Pergunta ao vivo (fase 2) é uma peça de infraestrutura nova (WhatsApp bidirecional + interpretação de intenção) — não expandir o conjunto de intenções além das 3 iniciais sem validação.
- Nicho ainda em validação prática — este documento assume e-commerce/marketplace como ponto de partida, mas a arquitetura (motor + fontes + canais) foi desenhada para ser agnóstica de nicho.

---

## 8. Referência de concorrência (contexto de mercado)

- **SellerHub Analytics**: integração OAuth com múltiplos marketplaces, IA conversacional dentro do painel, sem entrega proativa via WhatsApp, preço não público.
- **Nubimetrics**: foco em inteligência de mercado, preço sob consulta.
- **Sellerboard / Seller Fetch**: referência internacional, ticket de entrada baixo (US$ 9-19/mês).
- Faixa de preço sugerida pro plano de entrada, com base no mercado: R$ 47-97/mês.
