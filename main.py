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
    allow_origins=
    [
        "http://localhost:5173",
        "https://family-day-backend.onrender.com", 
        "https://52f3-211-23-70-114.ngrok-free.app"    
    ],
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)


@app.get("/health-check")
async def health_check():
    return "The API service is running!"
