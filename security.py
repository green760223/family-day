import datetime
import logging
import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt

from database import database, employee_table

logger = logging.getLogger(__name__)

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def access_token_expire_minutes() -> int:
    return ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(mobile: str):
    logger.debug("Creating access token", mobile={"mobile": mobile})
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    jwt_data = {"sub": mobile, "exp": expire}
    encoded_jwt = jwt.encode(jwt_data, key=SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def get_user(mobile: str):
    logger.debug("Getting user from the database", mobile={"mobile": mobile})
    query = employee_table.select().where(employee_table.c.mobile == mobile)
    result = await database.fetch_one(query)

    if result:
        return result


async def authenticate_user(mobile: str):
    logger.debug("Authenticating user", mobile={"mobile": mobile})
    user = await get_user(mobile)

    if not user:
        raise credentials_exception

    return user


async def get_current_employee(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        mobile: str = payload.get("sub")

        if mobile is None:
            raise credentials_exception

    except ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    except JWTError as e:
        raise credentials_exception from e

    employee = await get_user(mobile=mobile)

    if employee is None:
        raise credentials_exception
    return employee

async def verify_jwt_token(token: Annotated[str, Depends(oauth2_scheme)]):
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
