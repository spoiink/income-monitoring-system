from typing import Generator

from fastapi import Depends, HTTPException

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy.orm import Session

from app.database import SessionLocal
 
from app.models import User

from app.repository import users as users_repository



# Схема безопасности для HTTP Bearer токенов (токен передается в заголовке Authorization)
security = HTTPBearer()



def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# Функция для получения текущего пользователя из токена авторизации
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), 
                     db: Session = Depends(get_db)) -> User:
# Извлекаем логин из токена авторизации (токен передается в заголовке Authorization)
    login = credentials.credentials
# Ищем пользователя в базе данных по логину
    user = users_repository.get_user(db, login)
    if not user:
        raise HTTPException(status_code=401, detail='Unautorized')
# Возвращаем найденного пользователя
    return user


