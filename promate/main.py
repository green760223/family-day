from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import database
from routers.employee import router as employee_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI()

app.include_router(employee_router, prefix="/api/v1/employees")


@app.get("/")
async def health_check():
    return "The API service is running!"
