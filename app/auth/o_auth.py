import mysql.connector
import jwt
from jwt.exceptions import DecodeError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from starlette import status
from decouple import config
from app.models.models import UserSchema
from app.db.db_config import connect_to_db


JWT_SECRET = config("secret")
JWT_ALGORITHM = config("algorithm")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/api/token")


def check_user_exists(username: str, email: str):
    query = "SELECT * FROM users WHERE username = %s OR email = %s"
    user_data = (username, email)

    try:
        with connect_to_db() as cnx:
            with cnx.cursor(dictionary=True) as cursor:
                cursor.execute(query, user_data)
                user_in_db = cursor.fetchone()
            if user_in_db is None:
                return False
            return True

    except mysql.connector.Error as err:
        return {"error": str(err), "message": "Error while fetching user."}


def authenticate_user(username: str, password: str):
    query = "SELECT * FROM users WHERE username = %s"
    user_data = (username,)

    try:
        with connect_to_db() as cnx:
            with cnx.cursor(dictionary=True) as cursor:
                cursor.execute(query, user_data)
                user_in_db = cursor.fetchone()
            if user_in_db is None:
                return False
            if not bcrypt_context.verify(password, user_in_db["password"]):
                return False

        return user_in_db

    except mysql.connector.Error as err:
        return {"error": str(err), "message": "Error while fetching user."}


def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {"sub": username, "id": user_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {"username": username, "id": user_id}
    except DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
