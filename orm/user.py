from sqlalchemy import Column, Integer, String
from orm import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    email = Column(String)
    password = Column(String)
    salt = Column(String)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email
        }
