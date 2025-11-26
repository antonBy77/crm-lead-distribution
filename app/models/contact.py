from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from ..database import Base
import datetime

class Contact(Base):
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    source_id = Column(Integer, ForeignKey("sources.id"))
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=True)
    message = Column(String, nullable=True)
    contact_data = Column(String, nullable=True)  # Дополнительные данные обращения
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_processed = Column(Boolean, default=False)
    
    # Связи
    lead = relationship("Lead", back_populates="contacts")
    source = relationship("Source", back_populates="contacts")
    operator = relationship("Operator", back_populates="contacts")
