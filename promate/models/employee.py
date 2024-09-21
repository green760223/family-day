from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EmployeeCreate(BaseModel):
    name: str
    department: str
    employee_id: str
    family_count: int = 0


class EmployeeResponse(EmployeeCreate):
    id: int
    qr_code: Optional[str] = None
    checked_in: Optional[bool] = None
    checked_in_time: Optional[datetime] = None
    is_deleted: Optional[bool] = None
