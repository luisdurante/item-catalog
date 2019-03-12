import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    email = Column(String(250), primary_key = True)
    name = Column(String(250), nullable = False)
    picture = Column(String(500), nullable = False)


class Category(Base):
    __tablename__ = 'category'
    category_name = Column(String(120), nullable = False)
    id = Column(Integer, primary_key = True)

    @property
    def serialize(self):
        return {
            'category_name'    :self.category_name,
            'category_id'      :self.id,
        }

class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key = True)
    name = Column(String(250), nullable = False)
    description = Column(String(400))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_email = Column(String(250), ForeignKey('user.email'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name'          :self.name,
            'description'   :self.description,
            'category'      :self.category_id,
        }

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.create_all(engine)


