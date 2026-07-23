"""Cria as tabelas no banco configurado em DATABASE_URL.

Suficiente enquanto o schema ainda está mudando rápido. Quando estabilizar,
vale trocar por migrations de verdade com Alembic (já está nas dependências)
em vez de create_all.
"""

from app.db.base import Base, engine
from app.models import *  # noqa: F401,F403 — garante que todos os modelos estão registrados

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("Tabelas criadas (ou já existentes) em", engine.url)
