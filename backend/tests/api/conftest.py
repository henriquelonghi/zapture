import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_current_client, get_db
from app.db.base import Base
from app.main import app
from app.models import Client


@pytest.fixture()
def db_session():
    # StaticPool + check_same_thread=False: o TestClient roda os endpoints numa
    # worker thread separada (via anyio), então a mesma conexão :memory: precisa
    # ser compartilhada entre threads — senão cada thread vê um banco vazio.
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, future=True)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client_record(db_session):
    c = Client(name="Loja Teste")
    db_session.add(c)
    db_session.commit()
    return c


@pytest.fixture()
def api_client(db_session, client_record):
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_client] = lambda: client_record
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
