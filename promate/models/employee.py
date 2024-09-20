from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Employee(BaseModel):
    id: int | None = None
    name: str
    department: str
    employee_id: str
    family_count: int = 0
    qr_code: Optional[str] = None
    checked_in: bool = False
    checked_in_time: Optional[datetime] = None
    is_deleted: bool = False
