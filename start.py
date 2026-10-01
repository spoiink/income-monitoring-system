from fastapi import FastAPI


from app.api.v1.wallets import router as wallet_router
from app.api.v1.operations import router as operations_router
from app.api.v1.users import router as users_router
from app.database import Base, engine
from fastapi.staticfiles import StaticFiles



app = FastAPI()

app.include_router(wallet_router, prefix='/api/v1', tags=['wallet'])
app.include_router(operations_router, prefix='/api/v1', tags=['operations'])
app.include_router(users_router, prefix='/api/v1', tags=['users'])

app.mount("/static", StaticFiles(directory="app/static"), name="static")

Base.metadata.create_all(bind=engine)