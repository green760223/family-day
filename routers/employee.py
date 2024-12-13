import base64
import logging
from datetime import datetime
from io import BytesIO
from typing import Annotated

import pandas as pd
import qrcode
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import insert, select, func

from database import database, employee_table, notifications_table
from models.employee import EmployeeCreate, EmployeeIn, EmployeeResponse, Notification, NotificationCreate, NotificationResponse
from security import authenticate_user, create_access_token, get_current_employee, SECRET_KEY, ALGORITHM, credentials_exception
from jose import ExpiredSignatureError, JWTError, jwt
import pytz

logger = logging.getLogger(__name__)

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Create a QR code for the employee
def generate_qr_code(employee_data: EmployeeCreate):

    # minimal_employee_data = {
    #     "name": employee_data["name"],
    #     "family_employee": employee_data["family_employee"],
    #     "family_infant": employee_data["family_infant"],
    #     "family_child": employee_data["family_child"],
    #     "family_adult": employee_data["family_adult"],
    #     "family_elderly": employee_data["family_elderly"],
    #     "group": employee_data["group"],
    #     "is_checked": employee_data["is_checked"],
    # }

    base_url = "http://127.0.0.1:8000/api/v1/employee/{mobile}/check-in"
    check_in_url = base_url.format(mobile=employee_data["mobile"])

    # data = json.dumps(minimal_employee_data, ensure_ascii=False)
    file_path = f"qrcodes/qr_code_{employee_data['mobile']}.png"
    render_file_path = f"/qrcodes/qr_code_{employee_data['mobile']}.png"
    
    

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )

    # qr.add_data(data)
    qr.add_data(check_in_url)
    qr.make(fit=True)

    # Create an image from the QR Code instance
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(render_file_path)

    # Convert the image to a base64 string
    buffered = BytesIO()
    img.save(buffered, format="PNG")

    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return img_str


@router.post(
    "/batch-create-employees",
    response_model=str,
    status_code=status.HTTP_201_CREATED,
)
async def batch_create_employees(file: UploadFile):
    # Read the uploaded EXCEL file
    try:
        df = pd.read_excel(file.file, dtype={"mobile": str})
        print("==df==", df.head())
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to process the uploaded file: {str(e)}"
        )

    # Check if the required columns are present
    required_columns = {
        "name",
        "company",
        "department",
        "mobile",
        "group",
        "family_employee",
        "family_infant",
        "family_child",
        "family_adult",
        "family_elderly",
    }
    if not required_columns.issubset(df.columns):
        raise HTTPException(
            status_code=400,
            detail=f"Missing required columns. Required: {required_columns}",
        )

    # Read the EXCEL file and create a list of employee data
    employees = []
    for _, row in df.iterrows():
        employee_data = {
            "name": row["name"],
            "mobile": row["mobile"],
            "group": row["group"],
            "company": row["company"],
            "department": row["department"],
            "family_employee": row["family_employee"],
            "family_infant": row["family_infant"],
            "family_child": row["family_child"],
            "family_adult": row["family_adult"],
            "family_elderly": row["family_elderly"],
            "is_checked": False,
            "is_deleted": False,
            # "qr_code": generate_qr_code(row.to_dict()),
        }
        employees.append(employee_data)

    # Insert the employee data into the database
    query = insert(employee_table).values(employees)
    await database.execute(query)

    return "Batch employees data insert successfully"


@router.post(
    "/create-employees",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_employee(employee: EmployeeCreate):
    query = employee_table.insert().values(
        name=employee.name,
        mobile=employee.mobile,
        department=employee.department,
        company=employee.company,
        family_employee=employee.family_employee,
        family_infant=employee.family_infant,
        family_child=employee.family_child,
        family_adult=employee.family_adult,
        family_elderly=employee.family_elderly,
        group=employee.group,
        is_checked=employee.is_checked,
        is_deleted=employee.is_deleted,
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


@router.get("/group/members/{group}", response_model=list[EmployeeResponse])
async def get_team_members(group: str):
    query = employee_table.select().where(employee_table.c.group == group)
    employees = await database.fetch_all(query)

    if not employees:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No employees found"
        )

    return [EmployeeResponse(**employee) for employee in employees]

@router.get("/total/participants", response_model=dict)
async def get_total_of_participants():
    query = select(
        func.sum(employee_table.c.family_employee).label("total_employee"),
        func.sum(employee_table.c.family_infant).label("total_infant"),
        func.sum(employee_table.c.family_child).label("total_child"),
        func.sum(employee_table.c.family_adult).label("total_adult"),
        func.sum(employee_table.c.family_elderly).label("total_elderly"),
    ).where(employee_table.c.is_checked == True)

    result = await database.fetch_one(query)

    return {
        "total_employee": result["total_employee"] or 0,
        "total_infant": result["total_infant"] or 0,
        "total_child": result["total_child"] or 0,
        "total_adult": result["total_adult"] or 0,
        "total_elderly": result["total_elderly"] or 0,
    }


@router.get("/{mobile}", response_model=EmployeeResponse)
async def get_employee(mobile: str, current_employee: Annotated[EmployeeIn, Depends(get_current_employee)]):
    print("===mobile===", mobile)
    if mobile != current_employee.mobile:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to view this employee",
        )
        
    query = employee_table.select().where(employee_table.c.mobile == mobile)
    employee = await database.fetch_one(query)

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found"
        )

    return EmployeeResponse(**employee)


# Check in an employee
@router.post("/{mobile}/check-in", response_model=EmployeeResponse, status_code=200)
async def check_in_employee(
    mobile: str,
    current_employee: Annotated[EmployeeIn, Depends(get_current_employee)],
):
    if mobile != current_employee.mobile:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to check in this employee",
        )

    query = employee_table.select().where(
        employee_table.c.mobile == current_employee.mobile
    )
    employee = await database.fetch_one(query)

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found"
        )

    tz = pytz.timezone("Asia/Taipei")
    taipei_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

    update_query = (
        employee_table.update()
        .where(employee_table.c.mobile == current_employee.mobile)
        .values(is_checked=True, checked_in_time=taipei_time)
    )
    await database.execute(update_query)

    updated_employee = await database.fetch_one(query)

    return EmployeeResponse(**updated_employee)


@router.post("/token")
async def login(employee: EmployeeIn):
    employee = await authenticate_user(employee.mobile)
    access_token = create_access_token(employee.mobile)
    print("==access_token==", access_token)

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/token/verify")
async def verify_token(token: Annotated[str, Depends(oauth2_scheme)]):
    print("==token==", token)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("==payload==", payload)
        return payload
    except ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except JWTError as e:
        raise credentials_exception from e


@router.post("/notifications/", response_model=NotificationResponse)
async def create_notification(notification: NotificationCreate):
    """
    新增公告
    """
    tz = pytz.timezone("Asia/Taipei")
    taipei_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    
    query = notifications_table.insert().values(
        title=notification.title,
        message=notification.message,
        created_at=taipei_time
    )
    
    last_record_id = await database.execute(query)
    
    return {
        "id": last_record_id,
        "title": notification.title,
        "message": notification.message,
        "created_at": notification.created_at   # 確保返回 created_at
    }


@router.get("/notifications/latest/", response_model=Notification)
async def get_latest_notification():
    """
    獲取最新公告
    """
    query = (
        notifications_table.select()
        .order_by(notifications_table.c.created_at.desc())
        .limit(1)
    )
    result = await database.fetch_one(query)
    if not result:
        raise HTTPException(status_code=404, detail="目前沒有任何公告")
    return result

