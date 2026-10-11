# conftest.py — at the backend/ root.
# Pytest reads this file automatically before collecting tests.
# Adding the backend directory to sys.path ensures `import app` works
# regardless of how pytest is invoked.

import sys
import os

# Insert the directory containing this file (backend/) at the front of the path.
sys.path.insert(0, os.path.dirname(__file__))

# ─── Shared in-memory database for the full test session ─────────────────────
# Both test_phase7_plans and test_phase8_integration need to write to the DB.
# We set up ONE engine here and override app.dependency_overrides[get_db] once,
# so there's no conflict between modules fighting over the same app singleton.

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import get_db
from app.db.models import Base

_TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestSession = sessionmaker(autocommit=False, autoflush=False, bind=_TEST_ENGINE)

# Create tables once for the entire pytest session
Base.metadata.create_all(bind=_TEST_ENGINE)


def _test_get_db():
    db = _TestSession()
    try:
        yield db
    finally:
        db.close()


# Register the override at session start — only one override, one engine.
app.dependency_overrides[get_db] = _test_get_db


@pytest.fixture(autouse=True)
def _clean_db():
    """Wipe all table rows before every test to ensure isolation."""
    with _TEST_ENGINE.begin() as conn:
        conn.execute(text("DELETE FROM action_plans"))
    yield
