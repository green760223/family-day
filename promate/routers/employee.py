import logging

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.sql import select

from database import database, employee_table
from models.employee import EmployeeCreate, EmployeeResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/create-employees",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_employee(employee: EmployeeCreate):
    query = employee_table.insert().values(
        name=employee.name,
        department=employee.department,
        employee_id=employee.employee_id,
        family_count=employee.family_count,
    )
    last_record_id = await database.execute(query)

    return {**employee.model_dump(), "id": last_record_id}


@router.get("/all-employees", response_model=list[EmployeeResponse])
async def get_all_employees():

    query = employee_table.select()
    employees = await database.fetch_all(query)

    if not employees:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No employees found"
        )

    return [EmployeeResponse(**employee) for employee in employees]


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(employee_id: str):
    query = employee_table.select().where(employee_table.c.employee_id == employee_id)
    employee = await database.fetch_one(query)

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found"
        )

    return EmployeeResponse(**employee)
