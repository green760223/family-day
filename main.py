import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import database
from routers.employee import router as employee_router
from starlette.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)

app.include_router(employee_router, prefix="/api/v1/employee")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://family-day-backend.onrender.com"],  # 允許所有來源，這對於開發環境很有用
    allow_credentials=True,
    allow_methods=["*"],  # 允許所有 HTTP 方法
    allow_headers=["*"],  # 允許所有 HTTP 標頭
)


@app.get("/health-check")
async def health_check():
    return "The API service is running!"
