from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..models import Lead
from ..schemas import LeadCreate

class LeadCRUD:
    def create_lead(self, db: Session, lead: LeadCreate) -> Lead:
        db_lead = Lead(**lead.dict())
        db.add(db_lead)
        db.commit()
        db.refresh(db_lead)
        return db_lead
    
    def get_lead(self, db: Session, lead_id: int) -> Lead:
        return db.query(Lead).filter(Lead.id == lead_id).first()
    
    def get_lead_by_external_id(self, db: Session, external_id: str) -> Lead:
        return db.query(Lead).filter(Lead.external_id == external_id).first()
    
    def get_leads(self, db: Session, skip: int = 0, limit: int = 100) -> list[Lead]:
        return db.query(Lead).offset(skip).limit(limit).all()
    
    def find_lead(self, db: Session, phone: str = None, email: str = None) -> Lead:
        conditions = []
        if phone:
            conditions.append(Lead.phone == phone)
        if email:
            conditions.append(Lead.email == email)
        
        if conditions:
            return db.query(Lead).filter(or_(*conditions)).first()
        return None
    
    def get_lead_contacts(self, db: Session, lead_id: int) -> list:
        return db.query(Lead).filter(Lead.id == lead_id).first().contacts if db.query(Lead).filter(Lead.id == lead_id).first() else []
