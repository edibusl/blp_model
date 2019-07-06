from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from orm import Base
from orm.level import BlpLevel


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    level = Column(Enum(BlpLevel), default=BlpLevel.UNCLASSIFIED)
    email = Column(String)
    password = Column(String)
    salt = Column(String)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'level': self.level.name
        }
