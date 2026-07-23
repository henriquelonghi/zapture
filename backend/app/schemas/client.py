import uuid

from pydantic import BaseModel


class ClientOut(BaseModel):
    id: uuid.UUID
    name: str
    whatsapp_phone: str | None

    model_config = {"from_attributes": True}


class ClientUpdateIn(BaseModel):
    whatsapp_phone: str | None = None
