from locale import currency

from pydantic import BaseModel, Field, field_validator

from decimal import Decimal

from app.enum import CurrencyEnum 

from datetime import datetime




class OperationRequest(BaseModel):
    wallet_name: str = Field(..., max_length=127)
    amount: Decimal
    description: str | None = Field(None, max_length=255)

            # Валидатор для проверки что сумма положительная
    @field_validator("amount")
    def amount_must_be_pos(cls, v: Decimal) -> Decimal:
            # Проверяем что значение больше нуля
        if v <= 0:
            # Если нет - выбрасываем ошибку валидации
            raise ValueError("Amount must be positive")
            # В ином случае возвращаем значение
        return v

    
            # Валидатор для проверки что имя кошелька не пустое
    @field_validator("wallet_name")
    def wallet_name_not_epmty(cls, v: str) -> str:
            # Убираем пробелы по краям
        v = v.strip()
            # Проверяем что строка не пустая
        if not v:
            # Если пустая - выбрасываем ошибку валидации
            raise ValueError("Wallet cannot be empty")
            # Возвращаем очищенное значение
        return v



            # Модель для создания кошелька
class CreateWalletRequest(BaseModel):
    name: str = Field(..., max_length=127)
    initial_balance: Decimal = 0

    currency: CurrencyEnum = CurrencyEnum.RUB



    @field_validator("name")
    def name_not_epmty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Wallet's name cannot be empty")
        return v



    @field_validator("initial_balance")
    def balance_not_negative(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("Initial balance cannot be negative")
        return v


class UserRequest(BaseModel):
    login: str = Field(..., max_length=127)


class UserResponse(UserRequest): 
    model_config = {'from_attributes': True}
    id: int


class WalletResponse(BaseModel):
    model_config = {'from_attributes': True} 
    id: int
    name: str
    balance: Decimal
    currency: CurrencyEnum


class OperationResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    wallet_id: int
    type: str
    amount: Decimal
    currency: CurrencyEnum
    category: str | None
    subcategory: str | None
    created_at: datetime


# Модель для создания перевода между кошельками
class TransferCreateSchema(BaseModel):  # Идентификатор кошелька, с которого переводим деньги
    from_wallet_id: int                 # Идентификатор кошелька, на который переводим деньги
    to_wallet_id: int
    # Сумма перевода
    amount: Decimal

    # Валидатор для проверки что кошельки разные
    @field_validator("to_wallet_id")
    @classmethod
    def wallets_must_differ(
        cls, v: int, info
    ) -> int:
        # Проверяем что целевой кошелек отличается от исходного
        if "from_wallet_id" in info.data and v == info.data["from_wallet_id"]:
            # Если кошельки одинаковые - выбрасываем ошибку валидации
            raise ValueError("Same wallets ids!")
        # Возвращаем значение если все ок
        return v


class TotalBalance(BaseModel):
    total_balance: Decimal