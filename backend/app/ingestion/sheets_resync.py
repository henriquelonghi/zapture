"""Resync automático do Google Sheets a cada abertura do relatório.

É essa peça que faz o Sheets ser mais "vivo" que o upload: como a fonte
permite releitura, a gente busca de novo a cada abertura. Se a
ressincronização falhar (credenciais ausentes, planilha desconectada, etc),
o relatório não deve quebrar — ele segue mostrando o último dado sincronizado
com sucesso, com um aviso explicando o motivo.
"""

from sqlalchemy.orm import Session

from app.core.google_credentials import get_google_service_account_credentials
from app.ingestion.pipeline import run_ingestion
from app.ingestion.sheets_source import SheetsSource
from app.models import Client, DataSourceConnection, DataSourceType


def resync_sheets_if_needed(db: Session, client: Client) -> str | None:
    connection = (
        db.query(DataSourceConnection)
        .filter(DataSourceConnection.client_id == client.id, DataSourceConnection.source_type == DataSourceType.SHEETS)
        .first()
    )
    if connection is None:
        return None

    spreadsheet_id = (connection.config or {}).get("spreadsheet_id")
    range_name = (connection.config or {}).get("range_name")
    if not spreadsheet_id or not range_name:
        return None

    credentials = get_google_service_account_credentials()
    if credentials is None:
        return "Não foi possível sincronizar com o Google Sheets agora (credenciais não configuradas no servidor)."

    source = SheetsSource(spreadsheet_id, range_name, credentials)
    try:
        outcome = run_ingestion(
            db,
            client.id,
            source,
            source_type=DataSourceType.SHEETS,
            source_label="Google Sheets",
            config=connection.config,
        )
    except Exception as exc:
        return f"Não foi possível sincronizar com o Google Sheets agora: {exc}"

    if not outcome.validation.is_valid:
        return "Planilha sincronizada, mas os dados não passaram na validação: " + "; ".join(outcome.validation.errors)

    return None
