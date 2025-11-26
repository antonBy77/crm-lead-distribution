from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uvicorn

from . import models, schemas, crud, services
from .database import engine, get_db, Base

# Создаем таблицы в БД
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CRM Lead Distribution", version="1.0.0")

# Инициализация CRUD
operator_crud = crud.OperatorCRUD()
lead_crud = crud.LeadCRUD()
source_crud = crud.SourceCRUD()
contact_crud = crud.ContactCRUD()

# Функция для получения сервиса распределения
def get_distribution_service():
    db = next(get_db())
    service = services.distribution.DistributionService(db)
    db.close()
    return service

# Эндпоинты для управления операторами
@app.post("/operators/", response_model=schemas.Operator)
def create_operator(operator: schemas.OperatorCreate, db: Session = Depends(get_db)):
    return operator_crud.create_operator(db=db, operator=operator)

@app.get("/operators/", response_model=List[schemas.Operator])
def read_operators(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    operators = operator_crud.get_operators(db, skip=skip, limit=limit)
    return operators

@app.get("/operators/{operator_id}", response_model=schemas.Operator)
def read_operator(operator_id: int, db: Session = Depends(get_db)):
    db_operator = operator_crud.get_operator(db, operator_id=operator_id)
    if db_operator is None:
        raise HTTPException(status_code=404, detail="Operator not found")
    return db_operator

@app.put("/operators/{operator_id}", response_model=schemas.Operator)
def update_operator(operator_id: int, operator: schemas.OperatorUpdate, db: Session = Depends(get_db)):
    db_operator = operator_crud.update_operator(db, operator_id=operator_id, operator=operator)
    if db_operator is None:
        raise HTTPException(status_code=404, detail="Operator not found")
    return db_operator

@app.delete("/operators/{operator_id}")
def delete_operator(operator_id: int, db: Session = Depends(get_db)):
    db_operator = operator_crud.delete_operator(db, operator_id=operator_id)
    if db_operator is None:
        raise HTTPException(status_code=404, detail="Operator not found")
    return {"message": "Operator deleted successfully"}

# Эндпоинты для управления весами операторов по источникам
@app.post("/operators/{operator_id}/sources/{source_id}/weight")
def set_operator_weight(operator_id: int, source_id: int, weight: float, db: Session = Depends(get_db)):
    db_weight = operator_crud.set_operator_weight(db, operator_id=operator_id, source_id=source_id, weight=weight)
    return {"message": "Weight set successfully", "weight": db_weight}

# Эндпоинты для управления источниками
@app.post("/sources/", response_model=schemas.Source)
def create_source(source: schemas.SourceCreate, db: Session = Depends(get_db)):
    return source_crud.create_source(db=db, source=source)

@app.get("/sources/", response_model=List[schemas.Source])
def read_sources(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sources = source_crud.get_sources(db, skip=skip, limit=limit)
    return sources

@app.get("/sources/{source_id}", response_model=schemas.Source)
def read_source(source_id: int, db: Session = Depends(get_db)):
    db_source = source_crud.get_source(db, source_id=source_id)
    if db_source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    return db_source

# Эндпоинты для лидов
@app.post("/leads/", response_model=schemas.Lead)
def create_lead(lead: schemas.LeadCreate, db: Session = Depends(get_db)):
    return lead_crud.create_lead(db=db, lead=lead)

@app.get("/leads/", response_model=List[schemas.Lead])
def read_leads(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    leads = lead_crud.get_leads(db, skip=skip, limit=limit)
    return leads

@app.get("/leads/{lead_id}", response_model=schemas.Lead)
def read_lead(lead_id: int, db: Session = Depends(get_db)):
    db_lead = lead_crud.get_lead(db, lead_id=lead_id)
    if db_lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return db_lead

@app.get("/leads/{lead_id}/contacts", response_model=List[schemas.Contact])
def read_lead_contacts(lead_id: int, db: Session = Depends(get_db)):
    contacts = lead_crud.get_lead_contacts(db, lead_id=lead_id)
    return contacts

# Эндпоинт для регистрации нового обращения
@app.post("/contacts/register/", response_model=schemas.Contact)
def register_contact(contact_data: schemas.ContactRegistration, db: Session = Depends(get_db)):
    distribution_service = get_distribution_service()
    
    try:
        contact = distribution_service.register_contact(contact_data)
        return contact
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Эндпоинты для обращений
@app.get("/contacts/", response_model=List[schemas.Contact])
def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    contacts = contact_crud.get_contacts(db, skip=skip, limit=limit)
    return contacts

@app.get("/contacts/{contact_id}", response_model=dict)
def read_contact_with_details(contact_id: int, db: Session = Depends(get_db)):
    contact = contact_crud.get_contact_with_details(db, contact_id=contact_id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@app.get("/operators/{operator_id}/contacts", response_model=List[schemas.Contact])
def read_operator_contacts(operator_id: int, db: Session = Depends(get_db)):
    contacts = contact_crud.get_contacts_by_operator(db, operator_id=operator_id)
    return contacts

@app.get("/sources/{source_id}/contacts", response_model=List[schemas.Contact])
def read_source_contacts(source_id: int, db: Session = Depends(get_db)):
    contacts = contact_crud.get_contacts_by_source(db, source_id=source_id)
    return contacts

# Эндпоинты для статистики и состояния
@app.get("/stats/operator-load")
def get_operator_load_stats(db: Session = Depends(get_db)):
    distribution_service = get_distribution_service()
    return distribution_service.get_operator_load_stats()

@app.get("/stats/unprocessed-contacts")
def get_unprocessed_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    contacts = contact_crud.get_unprocessed_contacts(db, skip=skip, limit=limit)
    return {"count": len(contacts), "contacts": contacts}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
