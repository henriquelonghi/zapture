# Especificação do MVP — SaaS de Relatórios e Insights de Faturamento

## 1. Contexto do produto

**Público-alvo (nicho de validação inicial):** sellers de e-commerce que vendem em marketplaces (Mercado Livre, Shopify, Nuvemshop), com foco em volume de aquisição via comunidades (Telegram/Facebook/WhatsApp de sellers).

**Proposta de valor central:**
> "Enquanto ferramentas tradicionais te dão um painel completo pra consultar, a gente te manda o que importa direto no WhatsApp, sem você precisar ir atrás."

**Diferencial frente à concorrência (ex: SellerHub Analytics, Nubimetrics):** entrega proativa via WhatsApp como canal principal, não só dashboard passivo. Preço público e simples.

**Meta de validação:** 10 clientes ativados (conectaram conta + receberam ao menos 2 resumos) no primeiro mês.

---

## 2. Escopo por fases

### Fase 1 — MVP
1. Landing page (aquisição/conversão)
2. Motor de dados (ingestão + validação + cálculo de métricas + priorização de insights)
3. Relatório **dinâmico** (calcula na hora que é aberto, não é uma foto estática)
4. Resumo periódico automático via WhatsApp

### Fase 2 — pós-validação
1. Pergunta ao vivo via WhatsApp (conjunto **fixo** de intenções, não NLU aberto):
   - "Qual foi o produto mais vendido até agora no mês?"
   - "Quantos de [produto] foram vendidos?"
   - "Qual o faturamento de hoje?"
2. Requer fonte de dado via **API de plataforma** (Sheets/upload não sustentam "hoje" de forma confiável)
3. Expansão de integrações (TikTok Shop, Shopee, Amazon, etc.)

**Regra de ouro entre fases:** o LLM (se usado) decide *qual pergunta é essa* (intenção), nunca *qual é a resposta* (o número). O número sempre vem do motor determinístico.

---

## 3. Métricas do motor (Fase 1)

**Camada financeira**
- Faturamento total do período + variação % vs. período anterior
- Margem/lucro por produto (requer custo/COGS cadastrado pelo cliente) + margem agregada do período
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

| Método | Atualização | Relatório dinâmico | Margem por produto | Pergunta ao vivo (fase 2) |
|---|---|---|---|---|
| Google Sheets | Quando o cliente edita a planilha | Sim | Sim (se custo cadastrado) | Não confiável |
| Upload CSV/XLSX | Manual, a cada novo upload | Sim | Sim (se custo cadastrado) | Não |
| API de plataforma (ML/Shopify/Nuvemshop) | Automática, alta frequência | Sim | Sim (se custo cadastrado) | Sim |

**Decisões de arquitetura:**
- Sheets é o método "planilha" oficial (permite releitura periódica via API do Google); upload de arquivo é fallback pra ativação rápida, sem sync automático.
- "Dinâmico" aqui significa: o motor recalcula a cada abertura do relatório, não que os dados cheguem sozinhos — a atualização real do dado depende do método escolhido.
- Mostrar timestamp de última atualização de forma persistente e discreta dentro do relatório (ex: "dado de: Google Sheets, sincronizado em [data/hora]").
- Validar estrutura esperada no momento da leitura (schema check) e avisar o cliente se uma coluna esperada não for encontrada — nunca deixar erro silencioso gerar número furado.

---

## 5. Arquitetura geral (alto nível)

```
[Google Sheets] ─┐
[Upload CSV/XLSX] ─┼─► [Motor de dados: valida + calcula métricas + prioriza insights] ─┬─► [Relatório dinâmico]
[API plataforma] ─┘                                                                      └─► [Resumo WhatsApp periódico]
```

- Um único motor de cálculo alimenta os dois canais de saída — não há duplicação de lógica entre relatório e resumo.
- Fase 2 adiciona um interpretador de intenção antes do motor, para o fluxo de pergunta-resposta via WhatsApp (fluxo bidirecional, requer webhook + conta WhatsApp Business API).

---

## 6. Onboarding — pontos a decidir/desenhar em seguida

- Contextualização estruturada do negócio (formulário, não texto livre) para calibrar o motor de regras.
- Escolha do método de importação com resumo curto de capacidades (não a tabela completa — 1 frase + ícone por método).
- Cadastro de custo/COGS por produto (fricção conhecida e aceita conscientemente — validar reação real do cliente nas entrevistas).

---

## 7. Riscos e trade-offs assumidos conscientemente

- Margem completa por produto aumenta fricção de ativação — decisão tomada de forma consciente, validar com clientes reais se a fricção compromete a meta de 10 ativações no mês 1.
- "Tempo real" de fato só existe com fonte de API de plataforma — Sheets/upload são "tão vivos quanto a última atualização do cliente".
- Pergunta ao vivo (fase 2) é uma peça de infraestrutura nova (WhatsApp bidirecional + interpretação de intenção) — não expandir o conjunto de intenções além das 3 iniciais sem validação.
- Nicho ainda em validação prática — este documento assume e-commerce/marketplace como ponto de partida, mas a arquitetura (motor + fontes + canais) foi desenhada para ser agnóstica de nicho.

---

## 8. Referência de concorrência (contexto de mercado)

- **SellerHub Analytics**: integração OAuth com múltiplos marketplaces, IA conversacional dentro do painel, sem entrega proativa via WhatsApp, preço não público.
- **Nubimetrics**: foco em inteligência de mercado, preço sob consulta.
- **Sellerboard / Seller Fetch**: referência internacional, ticket de entrada baixo (US$ 9-19/mês).
- Faixa de preço sugerida pro plano de entrada, com base no mercado: R$ 47-97/mês.
