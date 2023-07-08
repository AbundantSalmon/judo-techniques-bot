from contextlib import contextmanager

from config import DATABASE_URI
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

"""
Adapted from https://www.learndatasci.com/tutorials/using-databases-python-postgres-sqlalchemy-and-alembic/
"""

engine = create_engine(DATABASE_URI, future=True)

# Global session
Session = sessionmaker(bind=engine, future=True)

# Declarative base to be used with all models
Base = declarative_base()


@contextmanager
def session_scope():
    """
    Session scope to do operations, ensures rollback and close where appropriate
        with session_scope() as s:
    """
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def recreate_database():
    """
    WARNING, do not use lightly, consider effects with alembic
    """
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)  # create all tables that inherit Base
