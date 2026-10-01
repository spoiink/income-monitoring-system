from enum import StrEnum, auto

class CurrencyEnum(StrEnum):
    RUB = auto()
    USD = auto()
    EUR = auto()

# Создаём перечисление (enumeration) типов операций
class OperationType(StrEnum):
    EXPENSE = auto()  # Расход (трата денег)
    INCOME = auto()  # Доход (пополнение)
    TRANSFER = auto()  # Перевод между кошельками