"""Ingestão via webhook (Mercado Livre/Shopify/Nuvemshop): mesma validação e
normalização do pipeline de Sheets/upload (run_ingestion em pipeline.py), mas
sem o passo de sobrescrever `DataSourceConnection.config` — nas fontes
antigas, config guardava parâmetro de leitura (spreadsheet_id etc.); aqui
config guarda o access_token da conexão OAuth, e um evento de pedido não deve
apagar isso."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.ingestion.pipeline import IngestionOutcome
from app.ingestion.schema_validator import validate_rows
from app.models import DataSourceConnection, DataSourceType
from app.ingestion.normalizer import normalize_and_persist


def ingest_order_rows(
    db: Session,
    client_id,
    rows: list[dict],
    source_type: DataSourceType,
    source_label: str,
) -> IngestionOutcome:
    validation = validate_rows(rows)

    if not validation.is_valid:
        return IngestionOutcome(validation=validation, summary=None, data_source=None)

    summary = normalize_and_persist(db, client_id, validation.valid_rows)

    data_source = (
        db.query(DataSourceConnection)
        .filter(DataSourceConnection.client_id == client_id, DataSourceConnection.source_type == source_type)
        .first()
    )
    if data_source is not None:
        data_source.last_synced_at = datetime.now(timezone.utc)
        data_source.last_sync_label = source_label
        data_source.last_validation_warnings = validation.warnings
        db.commit()

    return IngestionOutcome(validation=validation, summary=summary, data_source=data_source)
