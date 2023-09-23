from src.connect import db
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP
from datetime import datetime

class ApproveRequests(db.Model):
    __tablename__ = 'Approve_requests'
    id = Column(Integer, primary_key=True)
    request_data = Column(String, name='request_data', nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
