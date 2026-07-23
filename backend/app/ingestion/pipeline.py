"""Pipeline único de ingestão (fetch -> valida -> normaliza -> registra
sincronização), reusado tanto pelo endpoint de upload quanto pelo resync
automático do Google Sheets — sem duplicar lógica entre as duas fontes."""

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.ingestion.base import IngestionSource
from app.ingestion.normalizer import NormalizationSummary, normalize_and_persist
from app.ingestion.schema_validator import ValidationResult, validate_rows
from app.models import DataSourceConnection, DataSourceType


@dataclass
class IngestionOutcome:
    validation: ValidationResult
    summary: NormalizationSummary | None
    data_source: DataSourceConnection | None


def run_ingestion(
    db: Session,
    client_id: uuid.UUID,
    source: IngestionSource,
    source_type: DataSourceType,
    source_label: str,
    config: dict | None = None,
) -> IngestionOutcome:
    rows = source.fetch_rows()
    validation = validate_rows(rows)

    if not validation.is_valid:
        return IngestionOutcome(validation=validation, summary=None, data_source=None)

    summary = normalize_and_persist(db, client_id, validation.valid_rows)

    data_source = (
        db.query(DataSourceConnection)
        .filter(DataSourceConnection.client_id == client_id, DataSourceConnection.source_type == source_type)
        .first()
    )
    if data_source is None:
        data_source = DataSourceConnection(client_id=client_id, source_type=source_type)
        db.add(data_source)

    data_source.config = config if config is not None else (data_source.config or {})
    data_source.last_synced_at = datetime.now(timezone.utc)
    data_source.last_sync_label = source_label
    data_source.last_validation_warnings = validation.warnings
    db.commit()

    return IngestionOutcome(validation=validation, summary=summary, data_source=data_source)
