from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..models import Contact
from ..schemas import ContactCreate, Contact as ContactSchema

class ContactCRUD:
    def create_contact(self, db: Session, contact: ContactCreate) -> Contact:
        db_contact = Contact(**contact.dict())
        db.add(db_contact)
        db.commit()
        db.refresh(db_contact)
        return db_contact
    
    def get_contact(self, db: Session, contact_id: int) -> Contact:
        return db.query(Contact).filter(Contact.id == contact_id).first()
    
    def get_contacts(self, db: Session, skip: int = 0, limit: int = 100) -> list[Contact]:
        return db.query(Contact).offset(skip).limit(limit).all()
    
    def get_contacts_by_lead(self, db: Session, lead_id: int) -> list[Contact]:
        return db.query(Contact).filter(Contact.lead_id == lead_id).all()
    
    def get_contacts_by_operator(self, db: Session, operator_id: int) -> list[Contact]:
        return db.query(Contact).filter(Contact.operator_id == operator_id).all()
    
    def get_contacts_by_source(self, db: Session, source_id: int) -> list[Contact]:
        return db.query(Contact).filter(Contact.source_id == source_id).all()
    
    def get_unprocessed_contacts(self, db: Session, skip: int = 0, limit: int = 100) -> list[Contact]:
        return db.query(Contact).filter(Contact.is_processed == False).offset(skip).limit(limit).all()
    
    def mark_contact_processed(self, db: Session, contact_id: int) -> Contact:
        contact = db.query(Contact).filter(Contact.id == contact_id).first()
        if contact:
            contact.is_processed = True
            db.commit()
            db.refresh(contact)
        return contact
    
    def get_contact_with_details(self, db: Session, contact_id: int) -> dict:
        contact = db.query(Contact).filter(Contact.id == contact_id).first()
        if not contact:
            return None
        
        return {
            "id": contact.id,
            "lead_id": contact.lead_id,
            "source_id": contact.source_id,
            "operator_id": contact.operator_id,
            "message": contact.message,
            "contact_data": contact.contact_data,
            "created_at": contact.created_at,
            "is_processed": contact.is_processed,
            "lead": {
                "id": contact.lead.id,
                "external_id": contact.lead.external_id,
                "phone": contact.lead.phone,
                "email": contact.lead.email,
                "name": contact.lead.name
            },
            "source": {
                "id": contact.source.id,
                "name": contact.source.name,
                "description": contact.source.description
            },
            "operator": {
                "id": contact.operator.id,
                "name": contact.operator.name,
                "is_active": contact.operator.is_active,
                "max_load": contact.operator.max_load
            } if contact.operator else None
        }
