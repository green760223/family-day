from fastapi import FastAPI

from promate.routers.employee import router as employee_router

app = FastAPI()

app.include_router(employee_router, prefix="/api/v1/employees")


@app.get("/")
async def health_check():
    return "The API service is running!"
