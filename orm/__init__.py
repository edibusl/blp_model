from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from orm.user import User
from orm.file import File

