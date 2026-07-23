from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_client, get_db
from app.core.google_credentials import get_google_service_account_credentials
from app.core.supabase_client import store_raw_upload
from app.ingestion.pipeline import run_ingestion
from app.ingestion.sheets_source import SheetsSource
from app.ingestion.upload_source import UploadSource
from app.models import Client, DataSourceConnection, DataSourceType
from app.schemas.ingestion import DataSourceOut, IngestionResultOut, SheetsConnectIn

router = APIRouter(prefix="/data-sources", tags=["data-sources"])


def _to_result_out(outcome) -> IngestionResultOut:
    return IngestionResultOut(
        orders_created=outcome.summary.orders_created,
        orders_updated=outcome.summary.orders_updated,
        items_created=outcome.summary.items_created,
        warnings=outcome.validation.warnings,
        row_errors=[f"linha {e.row_index + 1}: {e.message}" for e in outcome.validation.row_errors],
    )


@router.post("/upload", response_model=IngestionResultOut)
async def upload_sales_file(
    file: UploadFile,
    db: Session = Depends(get_db),
    client: Client = Depends(get_current_client),
) -> IngestionResultOut:
    content = await file.read()
    filename = file.filename or "arquivo"

    try:
        source = UploadSource(content, filename)
        outcome = run_ingestion(
            db,
            client.id,
            source,
            source_type=DataSourceType.UPLOAD,
            source_label=f"Upload: {filename}",
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if not outcome.validation.is_valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"errors": outcome.validation.errors, "warnings": outcome.validation.warnings},
        )

    store_raw_upload(str(client.id), filename, content)

    return _to_result_out(outcome)


@router.post("/sheets/connect", response_model=IngestionResultOut)
def connect_sheets(
    payload: SheetsConnectIn,
    db: Session = Depends(get_db),
    client: Client = Depends(get_current_client),
) -> IngestionResultOut:
    credentials = get_google_service_account_credentials()
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Credenciais de service account do Google não configuradas no servidor.",
        )

    source = SheetsSource(payload.spreadsheet_id, payload.range_name, credentials)

    try:
        outcome = run_ingestion(
            db,
            client.id,
            source,
            source_type=DataSourceType.SHEETS,
            source_label="Google Sheets",
            config={"spreadsheet_id": payload.spreadsheet_id, "range_name": payload.range_name},
        )
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if not outcome.validation.is_valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"errors": outcome.validation.errors, "warnings": outcome.validation.warnings},
        )

    return _to_result_out(outcome)


@router.get("", response_model=list[DataSourceOut])
def list_data_sources(
    db: Session = Depends(get_db),
    client: Client = Depends(get_current_client),
) -> list[DataSourceConnection]:
    return db.query(DataSourceConnection).filter(DataSourceConnection.client_id == client.id).all()
