from dataclasses import asdict
from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_client, get_db
from app.engine.report_service import generate_report
from app.ingestion.sheets_resync import resync_sheets_if_needed
from app.models import Client
from app.schemas.report import ReportOut

router = APIRouter(prefix="/report", tags=["report"])


@router.get("", response_model=ReportOut)
def get_report(
    period_start: date | None = None,
    period_end: date | None = None,
    db: Session = Depends(get_db),
    client: Client = Depends(get_current_client),
) -> ReportOut:
    """Recalcula o relatório na hora, a partir do dado normalizado mais recente.
    Se o cliente usa Google Sheets, tenta ressincronizar antes de calcular —
    é isso que faz essa fonte ser mais 'viva' que um upload manual."""

    end = period_end or date.today()
    start = period_start or (end - timedelta(days=29))

    resync_warning = resync_sheets_if_needed(db, client)

    report = generate_report(db, client.id, start, end)
    if resync_warning:
        report.validation_warnings.append(resync_warning)

    return ReportOut.model_validate(asdict(report))
