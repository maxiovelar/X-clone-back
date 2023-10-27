import mysql.connector

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.hash import bcrypt
from datetime import datetime, timedelta
from app.db.db_config import connect_to_db
from app.models.models import TweetSchema, UserSchema, TokenSchema

from app.auth.o_auth import (
    bcript_context,
    authenticate_user,
    create_access_token,
    get_current_user,
)

router = APIRouter(prefix="/api")


################################################################################
# Tweets routes
################################################################################


## Get all tweets
@router.get("/tweets", tags=["tweets"])
def get_tweets():
    query = "SELECT * FROM tweets"
    try:
        with connect_to_db() as cnx:
            with cnx.cursor(dictionary=True) as cursor:
                cursor.execute(query)
                response = cursor.fetchall()

            if not response:
                return {"message": "No tweets found."}

            return response

    except mysql.connector.Error as err:
        response = {"error": str(err), "message": "Error while fetching tweets."}

    return response


## Get single tweet by {id}
@router.get("/tweets/{id}", tags=["tweets"])
def get_tweet(id: int):
    query = "SELECT * FROM tweets WHERE id = %s"
    tweet_id = (id,)
    try:
        with connect_to_db() as cnx:
            with cnx.cursor(dictionary=True) as cursor:
                cursor.execute(query, tweet_id)
                response = cursor.fetchone()

            if response is None:
                return {"message": "Tweet not found."}

        return response

    except mysql.connector.Error as err:
        response = {"error": str(err), "message": "Error while fetching tweet."}

    return response


## Create new tweet
@router.post("/tweets", tags=["tweets"])
async def create_tweet(
    user=Depends(get_current_user), tweet: TweetSchema = Body(default=None)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    query = "INSERT INTO tweets (content) VALUES (%s)"
    tweet_content = (tweet.content,)
    try:
        with connect_to_db() as cnx:
            with cnx.cursor(dictionary=True) as cursor:
                cursor.execute(query, tweet_content)
                cnx.commit()

            if cursor.rowcount == 0:
                return {"message": "Tweet not created."}

        return {"message": "Tweet created successfully.", "user": user}

    except mysql.connector.Error as err:
        return {"error": str(err), "message": "Error while creating tweet."}


################################################################################
# Auth routes
################################################################################


## Register new user
@router.post("/auth/register", response_model=TokenSchema, tags=["auth"])
def create_user(user: UserSchema = Body(default=None)):
    hashed_password = bcript_context.hash(user.password)
    query = """
        INSERT INTO users (fullname, username, email, password)
        VALUES (%s, %s, %s, %s)
    """
    user_data = (user.fullname, user.username, user.email, hashed_password)

    try:
        with connect_to_db() as cnx:
            with cnx.cursor(dictionary=True) as cursor:
                cursor.execute(query, user_data)
                cnx.commit()

            if cursor.rowcount == 0:
                return {"message": "User not created."}

        token = create_access_token(user.username, user.id, timedelta(minutes=30))
        return {"access_token": token, "token_type": "bearer"}

    except mysql.connector.Error as err:
        return {"error": str(err), "message": "Error while creating user."}


## Get token (login)
@router.post("/token", response_model=TokenSchema, tags=["token"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token(user["username"], user["id"], timedelta(minutes=30))

    return {"access_token": token, "token_type": "bearer"}
