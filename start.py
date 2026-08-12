from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

BALANCE = {}


class OperationRequest(BaseModel):   
    wallet_name: str
    amount: float
    description: str | None = None



# ручка для возвращения балансов
@app.get('/balance')
def get_balance(wallet_name: str | None = None):
# Если имя кошелька не указано - считаем общий баланс
    if wallet_name is None:
        return {"total_balance": sum(BALANCE.values())}
# Проверяем существует ли запрашиваемый кошелек
    if wallet_name not in BALANCE:
        raise HTTPException(
            status_code=404,
            detail = f"Wallet '{wallet_name}' not found")

@app.post("/wallets/{name}")
def create_wallet(name:str, initial_balance: float=0):
# Проверяем не существует ли уже такой кошелек
    if name in BALANCE:
        raise HTTPException(
            status_code=400, 
        detail=f"Wallet '{name}' already exist"
        )
# Кошель создан, заполняем его началным балансом
    BALANCE[name] = initial_balance
# Возвращаем инфу о созданном кошельке
    return {
        'message': f"Your wallet '{name}' is ready for use",
            'wallet': name, 
            'balance': initial_balance
            }


# теперб мы создадим ручки для двух операций доходов и расходов с одной моделю
@app.post('/operations/income')
def add_income(operation: OperationRequest):
# Проверяем существует ли кошелек
    if operation.wallet_name not in BALANCE:
        raise HTTPException(
        status_code=404,
        detail=f"Wallet '{operation.wallet_name}' not found"
        )
        
# Проверяем что сумма положительная
    if operation.amount <= 0:
        raise HTTPException(
        status_code=400,
        detail="Amount must be positive"
        )    
# Добавляем доход к балансу кошелька
    BALANCE[operation.wallet_name] += operation.amount
# Возвращаем информацию об операции
    return {
        'message': 'Income added',
        'wallet': operation.wallet_name,
        "amount": operation.amount,
        'description': operation.description,
        'new_balance': BALANCE[operation.wallet_name]
    }
# Pасходы
@app.post('/operations/expense')
def add_expense(operation: OperationRequest):
# Проверяем существует ли кошелек
    if operation.wallet_name not in BALANCE:
        raise HTTPException(
            status_code=404,
            detail=f"Wallet '{operation.wallet_name}' not found"
        )
# Проверяем что сумма положительная
    if operation.amount <= 0:
        raise HTTPException(
        status_code=400,
        detail="Amount must be positive"
        ) 
# Проверяем достаточно ли средств в кошельке
    if BALANCE[operation.wallet_name] < operation.amount:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient funds. Available: {BALANCE[operation.wallet_name]}"
        )
        
# Вычитаем расход из баланса кошелька
    BALANCE[operation.wallet_name] -= operation.amount
# Возвращаем информацию об операции
    return {
        'message': 'Expense added',
        'wallet': operation.wallet_name,
        "amount": operation.amount,
        'description': operation.description,
        'new_balance': BALANCE[operation.wallet_name]
        } 
    