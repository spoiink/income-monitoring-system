from fastapi import APIRouter, Depends, Query

from datetime import datetime

from sqlalchemy.orm import Session

from app.dependency import get_db, get_current_user

from app.schemas import OperationRequest, OperationResponse, TransferCreateSchema

from app.service import operations as operations_service

from app.models import User




router = APIRouter()


@router.post("/operations/income", response_model=OperationResponse)
def add_income(operation: OperationRequest, db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    return operations_service.add_income(db, current_user, operation)


@router.post("/operations/expense", response_model=OperationResponse)
def add_expense(operation: OperationRequest, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    return operations_service.add_expense(db, current_user, operation)


@router.get("/operations", response_model=list[OperationResponse])
def get_operations_list(
    wallet_id: int | None = Query(None),  # Фильтр по идентификатору кошелька (необязательный параметр)
    date_from: datetime | None = Query(None),  # Фильтр по начальной дате (необязательный параметр)
    date_to: datetime | None = Query(None),  # Фильтр по конечной дате (необязательный параметр)
    user: User = Depends(get_current_user),  # Текущий пользователь из токена авторизации
    db: Session = Depends(get_db),  # Сессия базы данных
):
    return operations_service.get_operations_list(db, user, wallet_id, date_from, date_to)


@router.post("/operations/transfer", response_model=OperationResponse)
async def create_transfer(
    payload: TransferCreateSchema,  # Данные для перевода между кошельками
    user: User = Depends(get_current_user),  # Текущий пользователь из токена авторизации
    db: Session = Depends(get_db),  # Сессия базы данных
):
    # Вызываем сервис для перевода денег между кошельками
    return await operations_service.transfer_between_wallets(
        db,
        user.id,  # Идентификатор пользователя
        payload.from_wallet_id,  # Идентификатор кошелька-отправителя
        payload.to_wallet_id,  # Идентификатор кошелька-получателя
        payload.amount,  # Сумма перевода
    )