from sqlalchemy.orm import Session
from ..models import Source
from ..schemas import SourceCreate

class SourceCRUD:
    def create_source(self, db: Session, source: SourceCreate) -> Source:
        db_source = Source(**source.dict())
        db.add(db_source)
        db.commit()
        db.refresh(db_source)
        return db_source
    
    def get_source(self, db: Session, source_id: int) -> Source:
        return db.query(Source).filter(Source.id == source_id).first()
    
    def get_source_by_name(self, db: Session, name: str) -> Source:
        return db.query(Source).filter(Source.name == name).first()
    
    def get_sources(self, db: Session, skip: int = 0, limit: int = 100) -> list[Source]:
        return db.query(Source).offset(skip).limit(limit).all()
    
    def update_source(self, db: Session, source_id: int, source: SourceCreate) -> Source:
        db_source = db.query(Source).filter(Source.id == source_id).first()
        if db_source:
            update_data = source.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_source, key, value)
            db.commit()
            db.refresh(db_source)
        return db_source
    
    def delete_source(self, db: Session, source_id: int) -> Source:
        db_source = db.query(Source).filter(Source.id == source_id).first()
        if db_source:
            db.delete(db_source)
            db.commit()
        return db_source
