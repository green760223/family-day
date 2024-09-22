from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EmployeeCreate(BaseModel):
    name: str
    department: str
    employee_id: str
    family_count: int = 0
    checked_in: bool = False
    is_deleted: bool = False
    qr_code: Optional[str] = None


class EmployeeResponse(EmployeeCreate):
    id: int
    qr_code: Optional[str] = None
    checked_in: bool = False
    checked_in_time: Optional[datetime] = None
    is_deleted: bool = False
