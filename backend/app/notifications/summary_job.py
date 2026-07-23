"""Orquestra o resumo periódico via WhatsApp: para cada Client com telefone
cadastrado, resincroniza a fonte (mesma lógica do relatório dinâmico), roda o
motor e envia o resumo formatado. Pensado pra ser chamado por um agendador
externo (cron / Task Scheduler / cloud scheduler) via scripts/send_whatsapp_summaries.py
— não há scheduler in-process nesta etapa."""

import uuid
from dataclasses import dataclass
from datetime import date

from sqlalchemy.orm import Session

from app.engine.report_service import generate_report
from app.ingestion.sheets_resync import resync_sheets_if_needed
from app.models import Client
from app.notifications.summary_formatter import format_summary_message
from app.notifications.whatsapp_client import send_whatsapp_message


@dataclass
class SummaryResult:
    client_id: uuid.UUID
    client_name: str
    sent: bool
    reason: str | None = None


def send_periodic_summaries(
    db: Session, period_start: date, period_end: date, period_label: str = "ontem"
) -> list[SummaryResult]:
    clients = db.query(Client).filter(Client.whatsapp_phone.isnot(None)).all()

    results: list[SummaryResult] = []
    for client in clients:
        resync_sheets_if_needed(db, client)
        report = generate_report(db, client.id, period_start, period_end)
        message = format_summary_message(client.name, report, period_label=period_label)

        sent = send_whatsapp_message(client.whatsapp_phone, message)
        reason = None if sent else "envio falhou ou credenciais do WhatsApp não configuradas"
        results.append(SummaryResult(client_id=client.id, client_name=client.name, sent=sent, reason=reason))

    return results
