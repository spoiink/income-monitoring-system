from pydantic import BaseModel, Field, field_validator

class OperationRequest(BaseModel):
    wallet_name: str = Field(..., max_length=127)
    amount: float
    description: str | None = Field(None, max_length=255)

            # Валидатор для проверки что сумма положительная
    @field_validator("amount")
    def amount_must_be_pos(cls, v: float) -> float:
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
            # Название кошелька (обязательное поле, максимум 127 символов)
    name: str = Field(..., max_length=127)
            # Начальный баланс (необязательное поле, по умолчанию 0)
    initial_balance: float = 0

    @field_validator("name")
    def wallet_name_not_epmty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Wallet's name cannot be empty")
        return v

    @field_validator("initial_balance")
    def balance_not_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Initial balance cannot be negative")
        return v