from decimal import Decimal

from app.models import User, Wallet



def test_add_expense_success(db_session, client):
    # Arrange
    user = User(login="test")  # Создаем тестового пользователя
    db_session.add(user)  # Добавляем пользователя в сессию
    db_session.flush()  # Отправляем изменения в БД без commit
    wallet = Wallet(name="card", balance=200, user_id=user.id)  # Создаем кошелек с балансом 200
    db_session.add(wallet)  # Добавляем кошелек в сессию
    db_session.commit()  # Сохраняем изменения в базе данных
    db_session.refresh(wallet)  # Обновляем объект кошелька данными из БД

    # Act
    response = client.post(
        "/api/v1/operations/expense",  # Отправляем POST запрос на добавление расхода
        json={
            "wallet_name": "card",     
            "amount": 50.0,            
            "description": "Food"
        },
        headers={"Authorization": f"Bearer {user.login}"}  # Заголовок авторизации с логином пользователя
    )
    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == "Expense added"
    assert response.json()["wallet"] == wallet.name                      # Проверяем название кошелька в ответе
    assert Decimal(str(response.json()["amount"])) == Decimal(50)
    assert Decimal(str(response.json()["new_balance"])) == Decimal(150)  # Проверяем новый баланс (200 - 50 = 150)
    assert response.json()["description"] == "Food"


def test_add_expense_negative_amount(db_session, client):
    user = User(login='test')
    db_session.add(user)
    db_session.flush()
    wallet = Wallet(name='card', balance='200', user_id=user.id)
    db_session.add(wallet)
    db_session.commit()
    db_session.refresh(wallet)

    response = client.post(
        "/api/v1/operations/expense",
        json={
            "wallet_name": "card",
            "amount": -100.0,
            "description": "Food"
        },
        headers={"Authorization": f"Bearer {user.login}"}  # Заголовок авторизации с логином пользователя
    )
    # Assert
    assert response.status_code == 422


def test_add_expense_empty_name(db_session, client):
    user = User(login="test")
    db_session.add(user)
    db_session.flush()
    wallet = Wallet(name="card", balance=200, user_id=user.id)
    db_session.add(wallet)
    db_session.commit()
    db_session.refresh(wallet)

    response = client.post(
        "/api/v1/operations/expense",
        json={
            "wallet_name": "   ",
            "amount": 100.0, 
            "description": "Food"  
        },
        headers={"Authorization": f"Bearer {user.login}"}  
    )

    assert response.status_code == 422 


def test_add_expense_wallet_not_exist(db_session, client):
    user = User(login="test")
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/v1/operations/expense",
        json={
            "wallet_name": "card",
            "amount": 100.0,
            "description": "Food"
        },
        headers={"Authorization": f"Bearer {user.login}"}  # Заголовок авторизации с логином пользователя
    )

    assert response.status_code == 404


def test_add_expense_unauthorized(db_session, client):
    user = User(login="test")
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/v1/operations/expense",
        json={
            "wallet_name": "card",
            "amount": 100.0,
            "description": "Food"
        },
        headers={"Authorization": f"Bearer notexist"}  # Заголовок авторизации с логином пользователя
    )

    assert response.status_code == 401


def test_add_expense_not_enough_money(db_session, client):

    user = User(login="test")  
    db_session.add(user) 
    db_session.flush()  
    wallet = Wallet(name="card", balance=200, user_id=user.id)  
    db_session.add(wallet)  
    db_session.commit()  
    db_session.refresh(wallet) 

    
    response = client.post(
        "/api/v1/operations/expense",  
        json={
            "wallet_name": "card",     
            "amount": 250.0,            
            "description": "Food"
        },
        headers={"Authorization": f"Bearer {user.login}"}  
    )
   
    assert response.status_code == 400