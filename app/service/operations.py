from sqlalchemy.orm import Session

from datetime import datetime

from app.enum import OperationType

from app.schemas import OperationRequest, OperationResponse

from app.repository import wallets as wallets_repository

from fastapi import HTTPException

from app.models import User

from app.repository import operations as operations_repository

from decimal import Decimal

from app.service.exchange_service import get_exchange_rate




def add_income(db: Session, current_user: User, operation: OperationRequest) -> OperationResponse:
    # Проверяем существует ли кошелек
    if not wallets_repository.is_wallet_exist(db, current_user.id, operation.wallet_name):
        raise HTTPException(
            status_code=404,
            detail=f"Wallet '{operation.wallet_name}' not found"
        )
 
    # Валидация amount > 0 теперь в модели OperationRequest!
    # Добавляем доход к балансу кошелька через репозиторий
    wallet = wallets_repository.add_income(
        db, current_user.id, operation.wallet_name, operation.amount)
    # Создаем запись об операции дохода через репозиторий
    operation = operations_repository.create_operation(
        db=db,
        wallet_id=wallet.id,
        type=OperationType.INCOME,
        amount=operation.amount,  # Сумма операции
        currency=wallet.currency,  # Валюта операции (из кошелька)
    )
    # Сохраняем изменения в базе данных
    db.commit()
    # Возвращаем информацию об операции
    return OperationResponse.model_validate(operation)


def add_expense(db: Session, current_user: User, operation: OperationRequest) -> OperationResponse:
    if not wallets_repository.is_wallet_exist(
        db, current_user.id, operation.wallet_name
    ):
        raise HTTPException(
            status_code=404, detail=f"Wallet '{operation.wallet_name}' not found"
        )
    wallet = wallets_repository.get_wallet_balance_by_name(
        db, current_user.id, operation.wallet_name
    )
    if wallet.balance < operation.amount:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient funds. Available: {wallet.balance}",
        )
    wallet = wallets_repository.add_expense(
        db, current_user.id, operation.wallet_name, operation.amount
    )

    operation = operations_repository.create_operation(
        db=db,
        wallet_id=wallet.id,
        type=OperationType.EXPENSE,
        amount=operation.amount,  
        currency=wallet.currency,  
)
    db.commit()
    return OperationResponse.model_validate(operation)


def get_operations_list(
    db: Session,
    current_user: User,
    wallet_id: int | None = None,  # Фильтр по идентификатору кошелька (необязательный параметр)
    date_from: datetime | None = None,  # Фильтр по начальной дате (необязательный параметр)
    date_to: datetime | None = None  # Фильтр по конечной дате (необязательный параметр)
) -> list[OperationResponse]:
    
    # Если указан идентификатор кошелька - фильтруем по нему
    if wallet_id:
        # Получаем кошелек по идентификатору из репозитория
        wallet = wallets_repository.get_wallet_by_id(db, current_user.id, wallet_id)
        # Проверяем существует ли кошелек
        if not wallet:
            raise HTTPException(
                status_code=404,
                detail=f"Wallet '{wallet_id}' not found"
            )  # Если кошелька нет - возвращаем ошибку 404

        # Используем только указанный кошелек для фильтрации
        wallets_ids = [wallet.id]
    else:
        # Если кошелек не указан - получаем все кошельки пользователя
        wallets = wallets_repository.get_all_wallets(db, current_user.id)
        # Формируем список идентификаторов всех кошельков пользователя
        wallets_ids = [w.id for w in wallets]

    # Получаем список операций из репозитория с фильтрацией
    operations = operations_repository.get_operations_list(
        db,
        wallets_ids,  # Список идентификаторов кошельков для фильтрации
        date_from,  # Начальная дата для фильтрации
        date_to  # Конечная дата для фильтрации
    )
    # Преобразуем модели SQLAlchemy в модели Pydantic для ответа
    result = []
    for operation in operations:
        result.append(OperationResponse.model_validate(operation))
    return result



async def transfer_between_wallets(
    db: Session, user_id: int, from_wallet_id: int, to_wallet_id: int, amount: Decimal,
) -> OperationResponse:
    # Получаем кошелек-отправитель из репозитория
    from_wallet = wallets_repository.get_wallet_by_id(db, user_id, from_wallet_id)
    # Получаем кошелек-получатель из репозитория
    to_wallet = wallets_repository.get_wallet_by_id(db, user_id, to_wallet_id)

    # Проверяем что оба кошелька существуют
    if not from_wallet or not to_wallet:
        raise HTTPException(404, "Wallet not Found")  

    if from_wallet.balance < amount:
        raise HTTPException(
            400,
            f"Not enough money: {from_wallet.balance} {from_wallet.currency}",
        )

    # Изначально сумма для получателя равна сумме перевода
    target_amount = amount
    exchange_rate = 1.0
    if from_wallet.currency != to_wallet.currency:
        # Получаем курс обмена между валютами
        exchange_rate = await get_exchange_rate(
            from_wallet.currency, to_wallet.currency
        )
        # Конвертируем сумму по курсу
        target_amount = amount * exchange_rate

    # Списываем деньги с кошелька-отправителя
    from_wallet.balance = from_wallet.balance - amount
    # Зачисляем деньги на кошелек-получатель (с учетом конвертации если нужно)
    to_wallet.balance = to_wallet.balance + target_amount
    # Создаем запись об операции перевода через репозиторий
    operation = operations_repository.create_operation(
        db=db,
        wallet_id=from_wallet.id,  # Идентификатор кошелька-отправителя
        type=OperationType.TRANSFER,  # Тип операции - перевод
        amount=target_amount,  # Сумма операции (после конвертации если нужно)
        currency=to_wallet.currency,  # Валюта операции
    )
    db.add(from_wallet)  # Добавляем обновленный кошелек-отправитель в сессию
    db.add(to_wallet)  # Добавляем обновленный кошелек-получатель в сессию
    db.add(operation)  # Добавляем операцию в сессию
    db.commit()  # Сохраняем изменения в базе данных
    return OperationResponse.model_validate(operation)  # Возвращаем информацию об операции

    