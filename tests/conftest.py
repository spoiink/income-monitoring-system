from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from start import app
from app.database import Base
from app.dependency import get_db

# создаем соединение к базе  # указываем test.db в качестве пути к файлам
TEST_DATABASE_URL = "sqlite:///./test.db"


test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)


TestSessionLocal = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)


# Функция для получения сессии базы данных через dependency injection в FastAPI
def get_test_db() -> Generator[Session, None, None]:
    db = TestSessionLocal()
    try:
        # Возвращаем сессию через yield (это позволяет FastAPI автоматически закрыть сессию после использования)
        yield db
    finally:
        # Закрываем сессию базы данных в любом случае (даже если произошла ошибка)
        db.close()


app.dependency_overrides[get_db] = get_test_db


@pytest.fixture()
def client():
    yield TestClient(app)


@pytest.fixture(
    autouse=True
)  # autouse - объясняем что хотим запускать ее каждый раз независимо от теста
def setup_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()
