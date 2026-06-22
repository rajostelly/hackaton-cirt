from __future__ import annotations

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from aro.infrastructure.alerting.sqlalchemy_models import Base

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def _normalize_url(url: str) -> str:
    """Force le driver psycopg pour les URL Postgres « nues »."""
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    return url


def init_db(database_url: str) -> sessionmaker[Session]:
    """Initialise l'engine + la session factory et renvoie celle-ci.

    SQLite (dev/tests) : tables créées directement (idempotent). Postgres
    (prod) : schéma géré par les migrations Alembic — on ne crée rien ici afin
    que les migrations restent l'unique source de vérité.
    """
    global _engine, _session_factory
    if _engine is None:
        _engine = create_engine(_normalize_url(database_url), pool_pre_ping=True)
        _session_factory = sessionmaker(bind=_engine, expire_on_commit=False)
    if _engine.dialect.name == "sqlite":
        Base.metadata.create_all(_engine)
    assert _session_factory is not None
    return _session_factory


def reset_db() -> None:
    """Réinitialise l'état global (tests)."""
    global _engine, _session_factory
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _session_factory = None
