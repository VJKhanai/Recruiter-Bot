import pytest

import db
import seed
from app import app as flask_app


@pytest.fixture
def seeded_db(tmp_path, monkeypatch):
    """A fresh, fully seeded database in a temp folder for each test."""
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))
    db.init_schema()
    seed.seed()


@pytest.fixture
def client(seeded_db):
    return flask_app.test_client()