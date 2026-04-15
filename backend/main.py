from fastapi import FastAPI
from backend.api.routers.ai import router as airout
from backend.api.routers.stocks import router as stockrout

async def lifespan(app: FastAPI):
    print('Запуск программы')
    yield
    print('Закрытие программы')

app = FastAPI(title='Salesman')
app.include_router(airout)
app.include_router(stockrout)
@app.get('/')
async def status():
    return {'status': True}