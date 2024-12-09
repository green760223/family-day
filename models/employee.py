from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EmployeeCreate(BaseModel):
    name: str
    mobile: str
    department: str
    company: str
    family_employee: int = 1
    family_infant: Optional[int] = None
    family_child: Optional[int] = None
    family_adult: Optional[int] = None
    family_elderly: Optional[int] = None
    group: Optional[int] = None
    is_checked: bool = False
    is_deleted: bool = False


class EmployeeResponse(EmployeeCreate):
    id: int
    department: str
    company: str


class EmployeeIn(BaseModel):
    mobile: str
