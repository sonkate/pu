from src.connect import db
from sqlalchemy import Column, Integer, Sequence, String, Boolean, TIMESTAMP, BINARY
from datetime import datetime

class Users(db.Model):
    __tablename__ = 'Users'
    id = Column(Integer, primary_key=True)
    merchant_name = Column(String, name='merchant_name', nullable=True)
    email = Column(String, name='email', nullable=True)
    tax = Column(Integer, name='tax', nullable=True)
    address = Column(String, name='address', nullable=True)
    password = Column(BINARY, name='password', nullable=True)
    is_active = Column(Boolean, name='is_active', nullable=True, default=True)
    role = Column(String, name='role', nullable=True)
    legal_representative = Column(String, name='legal_representative', nullable=True)
    parent_tax = Column(Integer, name='parent_tax', nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)