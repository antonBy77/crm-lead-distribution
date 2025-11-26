from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from ..models import Operator, Lead, Source, Contact, OperatorSourceWeight
from ..schemas import ContactRegistration, Contact
import random

class DistributionService:
    def __init__(self, db: Session):
        self.db = db
    
    def find_or_create_lead(self, external_id: str = None, phone: str = None, email: str = None, name: str = None) -> Lead:
        """Находит существующего лида или создает нового"""
        
        # Ищем лид по внешнему ID, если он указан
        if external_id:
            lead = self.db.query(Lead).filter(Lead.external_id == external_id).first()
            if lead:
                return lead
        
        # Ищем лид по комбинации phone и email
        if phone or email:
            conditions = []
            if phone:
                conditions.append(Lead.phone == phone)
            if email:
                conditions.append(Lead.email == email)
            
            if conditions:
                lead = self.db.query(Lead).filter(or_(*conditions)).first()
                if lead:
                    return lead
        
        # Создаем нового лида
        lead_data = {}
        if external_id:
            lead_data["external_id"] = external_id
        if phone:
            lead_data["phone"] = phone
        if email:
            lead_data["email"] = email
        if name:
            lead_data["name"] = name
        
        lead = Lead(**lead_data)
        self.db.add(lead)
        self.db.commit()
        self.db.refresh(lead)
        return lead
    
    def get_available_operators_for_source(self, source_id: int) -> list[Operator]:
        """Возвращает список доступных операторов для источника"""
        
        # Получаем всех активных операторов для данного источника
        operator_weights = self.db.query(OperatorSourceWeight).filter(
            OperatorSourceWeight.source_id == source_id
        ).join(
            Operator, OperatorSourceWeight.operator_id == Operator.id
        ).filter(
            Operator.is_active == True
        ).all()
        
        if not operator_weights:
            return []
        
        # Фильтруем операторов, которые не превышают лимит нагрузки
        available_operators = []
        for ow in operator_weights:
            # Считаем текущую нагрузку оператора
            current_load = self.db.query(Contact).filter(
                Contact.operator_id == ow.operator_id,
                Contact.is_processed == False
            ).count()
            
            if current_load < ow.operator.max_load:
                available_operators.append((ow.operator, ow.weight))
        
        return available_operators
    
    def select_operator_by_weights(self, available_operators: list) -> Operator:
        """Выбирает оператора с учетом весов"""
        if not available_operators:
            return None
        
        # Вычисляем общий вес
        total_weight = sum(weight for _, weight in available_operators)
        
        # Генерируем случайное число
        random_value = random.uniform(0, total_weight)
        
        # Находим оператора
        current_weight = 0
        for operator, weight in available_operators:
            current_weight += weight
            if random_value <= current_weight:
                return operator
        
        # Возвращаем последнего оператора (на случай погрешностей округления)
        return available_operators[-1][0]
    
    def register_contact(self, contact_data: ContactRegistration) -> Contact:
        """Регистрирует новое обращение и распределяет его между операторами"""
        
        # Находим или создаем лида
        lead = self.find_or_create_lead(
            external_id=contact_data.external_id,
            phone=contact_data.phone,
            email=contact_data.email,
            name=contact_data.name
        )
        
        # Находим источник
        source = self.db.query(Source).filter(Source.id == contact_data.source_id).first()
        if not source:
            raise ValueError(f"Source with id {contact_data.source_id} not found")
        
        # Получаем доступных операторов
        available_operators = self.get_available_operators_for_source(contact_data.source_id)
        
        # Выбираем оператора
        operator = None
        if available_operators:
            operator = self.select_operator_by_weights(available_operators)
        
        # Создаем обращение
        contact = Contact(
            lead_id=lead.id,
            source_id=source.id,
            operator_id=operator.id if operator else None,
            message=contact_data.message,
            contact_data=contact_data.contact_data
        )
        
        self.db.add(contact)
        self.db.commit()
        self.db.refresh(contact)
        
        return contact
    
    def get_operator_load_stats(self) -> dict:
        """Возвращает статистику нагрузки по операторам"""
        stats = []
        
        operators = self.db.query(Operator).all()
        for operator in operators:
            current_load = self.db.query(Contact).filter(
                Contact.operator_id == operator.id,
                Contact.is_processed == False
            ).count()
            
            stats.append({
                "operator_id": operator.id,
                "operator_name": operator.name,
                "max_load": operator.max_load,
                "current_load": current_load,
                "load_percentage": (current_load / operator.max_load * 100) if operator.max_load > 0 else 0
            })
        
        return stats
