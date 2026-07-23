import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import JSON, DateTime, ForeignKey, String, Uuid
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DataSourceType(str, Enum):
    SHEETS = "sheets"
    UPLOAD = "upload"


class DataSourceConnection(Base):
    """Config de uma fonte de dados conectada por um Client + timestamp da última sincronização."""

    __tablename__ = "data_source_connections"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), index=True)
    source_type: Mapped[DataSourceType] = mapped_column(SAEnum(DataSourceType), nullable=False)
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_sync_label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_validation_warnings: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
