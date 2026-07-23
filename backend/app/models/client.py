import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Client(Base):
    """Um workspace/seller cadastrado no SaaS (raiz de tenancy)."""

    __tablename__ = "clients"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255))
    whatsapp_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    """Número em formato E.164 (ex: 5511999998888). Sem isso, o cliente não
    entra no job de resumo periódico — só recebe o relatório dinâmico."""
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    members: Mapped[list["ClientMember"]] = relationship(back_populates="client", cascade="all, delete-orphan")


class ClientMember(Base):
    """Liga um usuário autenticado (Supabase Auth) a um Client."""

    __tablename__ = "client_members"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), index=True)
    supabase_user_id: Mapped[str] = mapped_column(String(255), index=True)
    role: Mapped[str] = mapped_column(String(50), default="owner")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    client: Mapped["Client"] = relationship(back_populates="members")
