from fastapi import APIRouter, Body, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.models.models import TweetSchema, UserSchema, TokenSchema

from app.auth.o_auth import get_current_user

from app.services.services import (
    get_tweets,
    get_tweet,
    create_tweet,
    create_user,
    login,
)

router = APIRouter(prefix="/api")


################################################################################
# Tweets routes
################################################################################


## Get all tweets
@router.get("/tweets", tags=["tweets"])
def get_all_tweets():
    return get_tweets()


## Get single tweet by {id}
@router.get("/tweets/{id}", tags=["tweets"])
def get_single_tweet(id: int):
    return get_tweet(id)


## Create new tweet
@router.post("/tweets", tags=["tweets"])
async def create_new_tweet(
    user=Depends(get_current_user), tweet: TweetSchema = Body(default=None)
):
    return await create_tweet(user, tweet)


################################################################################
# Auth routes
################################################################################


## Register new user
@router.post("/auth/register", response_model=TokenSchema, tags=["auth"])
def register_user(user: UserSchema = Body(default=None)):
    return create_user(user)


## Get token (login)
@router.post("/token", response_model=TokenSchema, tags=["token"])
async def user_login(form_data: OAuth2PasswordRequestForm = Depends()):
    return await login(form_data.username, form_data.password)
