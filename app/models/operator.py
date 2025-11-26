from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class Operator(Base):
    __tablename__ = "operators"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    max_load = Column(Integer, default=10)
    
    # Связи
    contacts = relationship("Contact", back_populates="operator")
    source_weights = relationship("OperatorSourceWeight", back_populates="operator")

class OperatorSourceWeight(Base):
    __tablename__ = "operator_source_weights"
    
    id = Column(Integer, primary_key=True, index=True)
    operator_id = Column(Integer, ForeignKey("operators.id"))
    source_id = Column(Integer, ForeignKey("sources.id"))
    weight = Column(Float, default=1.0)
    
    # Связи
    operator = relationship("Operator", back_populates="source_weights")
    source = relationship("Source", back_populates="operator_weights")
