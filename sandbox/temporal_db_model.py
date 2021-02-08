import os
from datetime import datetime, timedelta

import google.auth
from google.cloud import secretmanager
from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer, String,
                        Text, create_engine, engine, Computed, JSON, MetaData)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, backref
from sqlalchemy.sql import func, false, text
from uuid import uuid4

db_url = engine.url.URL(
    drivername=os.getenv('DRIVER_NAME'),
    username= os.getenv('DB_USER'),
    password= os.getenv('DB_PASSWORD'),
    database= 'sandbox',
    host= os.getenv('DB_HOST'),
    port= os.getenv('DB_PORT')
)

engine = create_engine(db_url)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Person(Base):
    __tablename__ = 'person'

    def __init__(self, person_id, name, city):
        self.person_id = person_id
        self.name = name
        self.city = city

    person_id = Column(String(36), primary_key=True)
    valid_from = Column(DateTime, server_default=func.now())
    valid_to = Column(DateTime, server_default=datetime.max, nullable=False)

    name = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)

    def update_city(self, city, session):
        self.valid_to = datetime.now()
        new_person = Person(str(uuid4()), self.name, city)
        session.add(new_person)
        session.commit()
        return
