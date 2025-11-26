from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from ..database import Base
import datetime

class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, index=True, unique=True)  # Внешний ID для идентификации лида
    phone = Column(String, index=True, nullable=True)
    email = Column(String, index=True, nullable=True)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Связи
    contacts = relationship("Contact", back_populates="lead")
