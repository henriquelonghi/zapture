import uuid

from pydantic import BaseModel


class ProductOut(BaseModel):
    id: uuid.UUID
    sku: str | None
    name: str
    category: str | None
    unit_cost: float | None


class ProductCostIn(BaseModel):
    unit_cost: float
