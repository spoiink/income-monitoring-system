from pytest import Session

from app.models import Operation

from decimal import Decimal

from app.enum import CurrencyEnum

from datetime import datetime


def create_operation(
    db: Session,
    wallet_id: int,
    type: str,
    amount: Decimal,
    currency: CurrencyEnum,
    category: str | None = None,
    subcategory: str | None = None,
) -> Operation:
   
    operation = Operation(
        wallet_id=wallet_id, 
        type=type, 
        amount=amount,  
        currency=currency, 
        category=category,  
        subcategory=subcategory,  
    )
    db.add(operation)  
    db.flush() 
    return operation 

def get_operations_list(
    db: Session,
    wallets_ids: list[int],  # Список идентификаторов кошельков для фильтрации
    date_from: datetime | None,  # Начальная дата для фильтрации (необязательный параметр)
    date_to: datetime | None,  # Конечная дата для фильтрации (необязательный параметр)
) -> list[Operation]:
    # Начинаем запрос к таблице операций
    # Фильтруем операции по списку идентификаторов кошельков
    query = db.query(Operation).filter(Operation.wallet_id.in_(wallets_ids))

    # Если указана начальная дата - добавляем фильтр по дате создания операции
    if date_from:
        query = query.filter(Operation.created_at >= date_from)

    # Если указана конечная дата - добавляем фильтр по дате создания операции
    if date_to:
        query = query.filter(Operation.created_at <= date_to)

    return query.all()