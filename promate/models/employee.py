from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EmployeeCreate(BaseModel):
    name: str
    mobile: str
    family_employee: int = 1
    family_infant: Optional[int] = None
    family_child: Optional[int] = None
    family_adult: Optional[int] = None
    family_elderly: Optional[int] = None
    is_checked: bool = False
    is_deleted: bool = False
    qr_code: Optional[str] = None


class EmployeeResponse(EmployeeCreate):
    id: int
    checked_in_time: Optional[datetime] = None
