from src.connect import db
from sqlalchemy import Column, Integer, Sequence, String

class Test(db.Model):
    __tablename__ = 'test'
    id = Column(Integer, Sequence(name='test_id',
                                  start=1, increment=1), primary_key=True)  
    
    name = Column(String, name='name', nullable=True)
    password = Column(String, name='password', nullable=True)