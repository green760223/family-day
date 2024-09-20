from fastapi import APIRouter

from models.employee import Employee

router = APIRouter()


@router.get("/")
async def health_check():
    return "The employees service is running!"


@router.get("/employees/{employee_id}", response_model=Employee)
async def get_employee(employee_id: int):
    return {"employee_id": employee_id}
