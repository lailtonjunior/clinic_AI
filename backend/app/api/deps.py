from typing import Generator
from app.database import get_db


def get_db_session() -> Generator:
    yield from get_db()
