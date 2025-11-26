from sqlalchemy.orm import Session
from ..models import Operator, OperatorSourceWeight
from ..schemas import OperatorCreate, OperatorUpdate

class OperatorCRUD:
    def create_operator(self, db: Session, operator: OperatorCreate) -> Operator:
        db_operator = Operator(**operator.dict())
        db.add(db_operator)
        db.commit()
        db.refresh(db_operator)
        return db_operator
    
    def get_operator(self, db: Session, operator_id: int) -> Operator:
        return db.query(Operator).filter(Operator.id == operator_id).first()
    
    def get_operators(self, db: Session, skip: int = 0, limit: int = 100) -> list[Operator]:
        return db.query(Operator).offset(skip).limit(limit).all()
    
    def update_operator(self, db: Session, operator_id: int, operator: OperatorUpdate) -> Operator:
        db_operator = db.query(Operator).filter(Operator.id == operator_id).first()
        if db_operator:
            update_data = operator.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_operator, key, value)
            db.commit()
            db.refresh(db_operator)
        return db_operator
    
    def delete_operator(self, db: Session, operator_id: int) -> Operator:
        db_operator = db.query(Operator).filter(Operator.id == operator_id).first()
        if db_operator:
            db.delete(db_operator)
            db.commit()
        return db_operator

    def set_operator_weight(self, db: Session, operator_id: int, source_id: int, weight: float) -> OperatorSourceWeight:
        # Удаляем старый вес, если он существует
        db_weight = db.query(OperatorSourceWeight).filter(
            OperatorSourceWeight.operator_id == operator_id,
            OperatorSourceWeight.source_id == source_id
        ).first()
        
        if db_weight:
            db_weight.weight = float(weight)
        else:
            db_weight = OperatorSourceWeight(
                operator_id=operator_id,
                source_id=source_id,
                weight=float(weight)
            )
            db.add(db_weight)
        
        db.commit()
        db.refresh(db_weight)
        return db_weight

    def get_operator_weights(self, db: Session, operator_id: int) -> list[OperatorSourceWeight]:
        return db.query(OperatorSourceWeight).filter(
            OperatorSourceWeight.operator_id == operator_id
        ).all()
