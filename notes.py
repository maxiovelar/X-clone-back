# import mysql.connector
# import colorama
# from fastapi import APIRouter, Request
# from app.db.db_config import connect_to_db
# from app.models.model import TweetSchema

# from colorama import Fore
# from colorama import Style


# colorama.init()

# router = APIRouter(prefix="/api")


# ################################################################################
# # Execute query on database
# ################################################################################
# def execute_query(query, params=None, fetchone=False):
#     try:
#         with connect_to_db() as cnx:
#             with cnx.cursor(dictionary=True) as cursor:
#                 cursor.execute(query, params)
#                 if fetchone:
#                     response = cursor.fetchone()
#                 else:
#                     response = cursor.fetchall()
#                 cnx.commit()
#                 print(
#                     f"{Fore.GREEN}DB_STATUS: Query executed successfully {Style.RESET_ALL}"
#                 )
#                 return response
#     except mysql.connector.Error as err:
#         print(
#             f"{Fore.RED}ERROR: Error while executing query: {query} {Style.RESET_ALL}"
#         )
#         print(Fore.RED + "{}".format(err) + Style.RESET_ALL)
#         response = {"error": str(err), "message": "Error while executing query."}
#         return response


# ################################################################################
# # Get all tweets
# ################################################################################
# @router.get("/tweets", tags=["tweets"])
# def get_tweets():
#     query = "SELECT * FROM tweets"
#     response = execute_query(query)
#     return response


# ################################################################################
# # Get single tweet by {id}
# ################################################################################
# @router.get("/tweets/{id}", tags=["tweets"])
# def get_tweet(id: int):
#     query = "SELECT * FROM tweets WHERE id = %s"
#     response = execute_query(query, params=id, fetchone=True)
#     if response is None:
#         print(f"{Fore.RED}ERROR: Tweet not found {Style.RESET_ALL}")
#         return {"message": "Tweet not found."}
#     return response


# ################################################################################
# # Create new tweet
# ################################################################################
# @router.post("/tweets", tags=["tweets"])
# def create_tweet(tweet: TweetSchema):
#     query = "INSERT INTO tweets (content) VALUES (%s)"
#     content = tweet.content
#     response = execute_query(query, params=content)
#     if response.get("error"):
#         return response
#     if response.get("rowcount") == 0:
#         print(f"{Fore.RED}ERROR: Tweet not created {Style.RESET_ALL}")
#         return {"message": "Tweet not created."}
#     return {"message": "Tweet created successfully."}


