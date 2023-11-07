import mysql.connector

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.hash import bcrypt
from datetime import datetime, timedelta
from starlette import status
from app.db.db_config import connect_to_db
from app.models.models import TweetSchema, UserSchema, TokenSchema

from app.auth.o_auth import (
    bcrypt_context,
    check_user_exists,
    authenticate_user,
    create_access_token,
    get_current_user,
)


## Get all tweets
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


## Register new user
def create_user(user: UserSchema = Body(default=None)):
    if type(user) is not UserSchema:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user data"
        )

    user_already_exists = check_user_exists(user.username, user.email)
    if user_already_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The username or email already exists",
        )

    hashed_password = bcrypt_context.hash(user.password)
    query = """
        INSERT INTO users (firstname, lastname, username, email, password)
        VALUES (%s, %s, %s, %s, %s)
    """
    user_data = (
        user.firstname,
        user.lastname,
        user.username.lower(),
        user.email,
        hashed_password,
    )

    try:
        with connect_to_db() as cnx:
            with cnx.cursor(dictionary=True) as cursor:
                print("USER_DATA", user_data)
                cursor.execute(query, user_data)
                cnx.commit()

            if cursor.rowcount == 0:
                return {"message": "User not created."}
        token = create_access_token(user.username, user.id, timedelta(minutes=30))
        return {"access_token": token, "token_type": "bearer"}

    except mysql.connector.Error as err:
        return {"error": str(err), "message": "Error while creating user."}


## Get token (login)
async def login(username, password):
    user = authenticate_user(username, password)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token(user["username"], user["id"], timedelta(minutes=30))

    return {"access_token": token, "token_type": "bearer"}
