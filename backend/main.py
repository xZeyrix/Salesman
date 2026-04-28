import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routers.ai import router as airout
from backend.api.routers.user import router as userrout
from backend.api.routers.stocks import router as stockrout
from backend.api.routers.internal import router as internalrout
from backend.core.database import db_begin
from backend.core.logger import setup_logging
from backend.services.alpaca_news import start_worker   # <- заменили finhub

import logging

setup_logging()
logger = logging.getLogger(__name__)


async def lifespan(app: FastAPI):
    logger.info("Запуск программы")
    await db_begin()
    worker_task = asyncio.create_task(start_worker())
    yield
    worker_task.cancel()
    logger.info("Закрытие программы")


app = FastAPI(title="Salesman", lifespan=lifespan, version="0.0.2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(userrout)
app.include_router(airout)
app.include_router(stockrout)
app.include_router(internalrout)


@app.get("/")
async def status():
    return {"status": True}