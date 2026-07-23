"""Dispara o resumo periódico via WhatsApp pra todos os clients com telefone
cadastrado. Pensado pra ser chamado uma vez por dia por um agendador externo
(cron, Windows Task Scheduler, cloud scheduler) — não há scheduler in-process
nesta etapa do MVP.

Uso:
    python scripts/send_whatsapp_summaries.py                # resume o dia de ontem
    python scripts/send_whatsapp_summaries.py 2026-07-21     # resume um dia específico
"""

import sys
from datetime import date, timedelta

from app.db.session import SessionLocal
from app.notifications.summary_job import send_periodic_summaries

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_day = date.fromisoformat(sys.argv[1])
    else:
        target_day = date.today() - timedelta(days=1)

    db = SessionLocal()
    try:
        results = send_periodic_summaries(db, period_start=target_day, period_end=target_day)
    finally:
        db.close()

    for result in results:
        status = "OK" if result.sent else f"FALHOU ({result.reason})"
        print(f"{result.client_name}: {status}")

    if not results:
        print("Nenhum client com whatsapp_phone cadastrado.")
