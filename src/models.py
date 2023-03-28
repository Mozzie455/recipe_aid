from .import db
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy_utils import JSONType
from sqlalchemy_utils import UUIDType
from sqlalchemy_utils import EmailType
import uuid


class User(db.Model):
    __tablename__ = 'users'

    user_id = Column(UUIDType(binary=False),
                     primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False)
    email = Column(EmailType, nullable=False)
    password = Column(String, nullable=False)
    date_created = Column(DateTime, default=datetime.now())
    date_updated = Column(DateTime, onupdate=datetime.now())

    def __repr__(self) -> str:
        return 'User>>> {self.username}'


class Recipe(db.Model):
    __tablename__ = 'recipe'

    recipe_id = Column(Integer, primary_key=True)
    recipe_name = Column(String, unique=True, nullable=False)
    serving_size = Column(Integer, nullable=False)
    cooking_time = Column(String, nullable=False)
    ingredients = Column((JSONType), nullable=False)
    instructions = Column((JSONType), nullable=False)

    def __repr__(self) -> str:
        return 'Recipe>>> {self.recipe_name}'
