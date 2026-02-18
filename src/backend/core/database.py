"""
Database connection and session management

Provides database engine, session factory, and connection utilities.
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

from .config import get_config
from .database_models import Base
from ...utils.logger import get_logger

logger = get_logger(__name__)


# Global engine and session factory
_engine: Engine | None = None
_SessionLocal: sessionmaker | None = None


def get_engine() -> Engine:
    """
    Get or create the database engine (singleton)

    Returns:
        SQLAlchemy Engine instance
    """
    global _engine

    if _engine is None:
        config = get_config()

        logger.info("creating_database_engine", url=config.database.url)

        # Build engine kwargs — SQLite uses SingletonThreadPool
        # which does not support pool_size / max_overflow
        engine_kwargs = {
            "echo": config.database.echo,
            "pool_pre_ping": True,
        }

        if "sqlite" not in config.database.url:
            engine_kwargs["pool_size"] = config.database.pool_size
            engine_kwargs["max_overflow"] = config.database.max_overflow

        _engine = create_engine(config.database.url, **engine_kwargs)

        # Enable foreign keys for SQLite
        if "sqlite" in config.database.url:

            @event.listens_for(_engine, "connect")
            def set_sqlite_pragma(dbapi_conn, connection_record):
                cursor = dbapi_conn.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

        logger.info("database_engine_created")

    return _engine


def get_session_factory() -> sessionmaker:
    """
    Get or create the session factory (singleton)

    Returns:
        SQLAlchemy sessionmaker
    """
    global _SessionLocal

    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        logger.info("session_factory_created")

    return _SessionLocal


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions

    Yields:
        SQLAlchemy Session

    Example:
        >>> with get_db_session() as session:
        ...     products = session.query(Product).all()
    """
    SessionLocal = get_session_factory()
    session = SessionLocal()

    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error("database_session_error", error=str(e))
        raise
    finally:
        session.close()


def create_tables() -> None:
    """
    Create all database tables

    This should be called during application initialization.
    """
    engine = get_engine()
    logger.info("creating_database_tables")

    Base.metadata.create_all(bind=engine)

    logger.info("database_tables_created")


def drop_tables() -> None:
    """
    Drop all database tables

    WARNING: This will delete all data!
    """
    engine = get_engine()
    logger.warning("dropping_database_tables")

    Base.metadata.drop_all(bind=engine)

    logger.warning("database_tables_dropped")


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI to inject database sessions

    Yields:
        SQLAlchemy Session

    Example:
        >>> @app.get("/products")
        >>> def get_products(db: Session = Depends(get_db)):
        ...     return db.query(Product).all()
    """
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
