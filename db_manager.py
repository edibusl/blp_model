import sys
from contextlib import contextmanager
from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


this = sys.modules[__name__]
this.engine = None
this.session_factory = None


def init(db_filename=None):
    if not db_filename:
        db_filename = "blp.db"
    this.engine = create_engine('sqlite:///{}'.format(db_filename), echo=True)

    this.session_factory = sessionmaker(bind=this.engine)

    # from sqlalchemy import Table, Column, Integer, String, MetaData
    # meta = MetaData()


@contextmanager
def session_scope():
    """
    Provide a transactional scope around a series of operations.
    Warning! This context operates on the main db, default schema!
    """
    session = this.session_factory()
    try:
        yield session
    except:
        session.rollback()
        raise
    finally:
        session.close()
