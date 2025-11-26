from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class Source(Base):
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)  # Название бота/источника
    description = Column(String, nullable=True)
    
    # Связи
    contacts = relationship("Contact", back_populates="source")
    operator_weights = relationship("OperatorSourceWeight", back_populates="source")
