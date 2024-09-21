import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import database
from routers.employee import router as employee_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI()

app.include_router(employee_router, prefix="/api/v1/employee")


@app.get("/health-check")
async def health_check():
    return "The API service is running!"
