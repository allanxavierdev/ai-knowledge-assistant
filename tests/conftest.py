import os

# Define o DATABASE_URL antes de qualquer import do app.
# Isso é necessário porque session.py cria o engine no momento do import.
# Se não fizéssemos isso aqui, o SQLAlchemy tentaria conectar ao Postgres.
os.environ.setdefault("DATABASE_URL", "sqlite://")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import Base, get_db

# StaticPool faz todas as "conexões" reutilizarem a mesma conexão real.
# Sem isso, sqlite:// cria um banco novo para cada conexão —
# conftest criaria as tabelas em um banco, e os testes usariam outro (vazio).
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def override_get_db():
    """
    Substitui o get_db real durante os testes.
    O FastAPI vai injetar essa sessão ao invés da sessão de produção.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_database():
    """
    Fixture que roda antes (e depois) de cada teste.
    - autouse=True: aplica automaticamente em todos os testes sem precisar declarar
    - Cria as tabelas antes do teste, apaga depois — cada teste começa com banco limpo
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """
    Fixture que fornece o cliente HTTP de teste com o override do banco aplicado.
    """
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
