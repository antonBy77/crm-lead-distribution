from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Схемы для операторов
class OperatorBase(BaseModel):
    name: str
    is_active: bool = True
    max_load: int = 10

class OperatorCreate(OperatorBase):
    pass

class OperatorUpdate(OperatorBase):
    pass

class Operator(OperatorBase):
    id: int
    
    class Config:
        from_attributes = True

# Схемы для лидов
class LeadBase(BaseModel):
    external_id: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    name: Optional[str] = None

class LeadCreate(LeadBase):
    pass

class Lead(LeadBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Схемы для источников
class SourceBase(BaseModel):
    name: str
    description: Optional[str] = None

class SourceCreate(SourceBase):
    pass

class Source(SourceBase):
    id: int
    
    class Config:
        from_attributes = True

# Схемы для весов операторов по источникам
class OperatorSourceWeightBase(BaseModel):
    operator_id: int
    source_id: int
    weight: float = 1.0

class OperatorSourceWeightCreate(OperatorSourceWeightBase):
    pass

class OperatorSourceWeight(OperatorSourceWeightBase):
    id: int
    
    class Config:
        from_attributes = True

# Схемы для обращений
class ContactBase(BaseModel):
    message: Optional[str] = None
    contact_data: Optional[str] = None

class ContactCreate(ContactBase):
    lead_id: int
    source_id: int

class Contact(ContactBase):
    id: int
    lead_id: int
    source_id: int
    operator_id: Optional[int] = None
    created_at: datetime
    is_processed: bool
    
    class Config:
        from_attributes = True

# Схема для регистрации нового обращения
class ContactRegistration(BaseModel):
    external_id: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    source_id: int
    message: Optional[str] = None
    contact_data: Optional[str] = None
