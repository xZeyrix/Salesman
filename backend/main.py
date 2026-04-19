from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from backend.api.routers.ai import router as airout
from backend.api.routers.user import router as userrout
from backend.api.routers.stocks import router as stockrout
from backend.api.routers.internal import router as internalrout
from backend.core.database import db_begin
async def lifespan(app: FastAPI):
    print('Запуск программы')
    await db_begin()
    yield
    print('Закрытие программы')

app = FastAPI(title='Salesman', lifespan=lifespan)
app.include_router(userrout)
app.include_router(airout)
app.include_router(stockrout)
app.include_router(internalrout)

@app.middleware('http')
async def main_middleware(request: Request, call_next):
    if request.url.path.startswith('/internal'):
        if not request.headers.get('Authorization', None):
            return JSONResponse(status_code=401,
                                content='У вас нет доступа')
    response = await call_next(request)
    return response

@app.get('/')
async def status():
    return {'status': True}