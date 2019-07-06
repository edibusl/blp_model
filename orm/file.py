from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from orm import Base
from orm.level import BlpLevel


class File(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String)
    level = Column(Enum(BlpLevel), default=BlpLevel.UNCLASSIFIED)

    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship('User')

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'level': self.level.name,
            'owner_id': self.owner_id
        }
