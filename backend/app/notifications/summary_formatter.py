"""Monta o texto do resumo periódico de WhatsApp a partir do `Report` que já
alimenta o relatório dinâmico — mesmo motor, sem duplicar cálculo (só formatação).

Sempre inclui o rótulo de "idade do dado" (mesma informação do LastSyncedBadge
do relatório): o resumo é reativo à última sincronização da fonte conectada,
não necessariamente ao dia de hoje, e isso precisa ficar explícito pro cliente
não achar que o número é sempre "ao vivo" quando a fonte é Sheets/upload."""

from app.engine.report_service import Report

_HEADLINE_CATEGORIES = {"faturamento", "ticket_medio", "pedidos"}

_INSIGHT_EMOJI = {
    "ranking": "📦",
    "margem_negativa": "⚠️",
    "clientes_sumidos": "👤",
}


def _variation_suffix(variation_pct: float | None) -> str:
    if variation_pct is None:
        return ""
    return f" ({variation_pct:+.1f}% vs. período anterior)"


def _freshness_line(report: Report) -> str:
    if report.last_synced_at is None:
        return "Nenhuma fonte de dados conectada ainda."
    formatted = report.last_synced_at.strftime("%d/%m/%Y %H:%M")
    source = report.last_sync_label or "fonte desconhecida"
    return f"dado de: {source}, sincronizado em {formatted}"


def format_summary_message(client_name: str, report: Report, period_label: str = "ontem") -> str:
    lines = [f"Bom dia! Aqui está o resumo de {period_label} para {client_name} 👋", ""]

    lines.append(f"💰 Faturamento: R$ {report.revenue.total_current:,.2f}{_variation_suffix(report.revenue.variation_pct)}")
    lines.append(f"🛒 {report.volume.orders_current} pedidos{_variation_suffix(report.volume.variation_pct)}")
    if report.ticket.average_current is not None:
        lines.append(f"🎯 Ticket médio: R$ {report.ticket.average_current:,.2f}{_variation_suffix(report.ticket.variation_pct)}")

    extra_insights = [i for i in report.insights if i.category not in _HEADLINE_CATEGORIES]
    if extra_insights:
        lines.append("")
        for insight in extra_insights:
            emoji = _INSIGHT_EMOJI.get(insight.category, "📌")
            lines.append(f"{emoji} {insight.title}: {insight.description}")

    lines.append("")
    lines.append(_freshness_line(report))

    return "\n".join(lines)
