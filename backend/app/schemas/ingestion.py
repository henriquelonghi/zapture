from datetime import datetime

from pydantic import BaseModel


class IngestionResultOut(BaseModel):
    orders_created: int
    orders_updated: int
    items_created: int
    warnings: list[str]
    row_errors: list[str]


class SheetsConnectIn(BaseModel):
    spreadsheet_id: str
    range_name: str = "A1:Z10000"


class DataSourceOut(BaseModel):
    source_type: str
    last_synced_at: datetime | None
    last_sync_label: str | None
    last_validation_warnings: list[str]

    model_config = {"from_attributes": True}
