import os
import mysql.connector
import colorama
from mysql.connector import errorcode
from decouple import config
from colorama import Fore
from colorama import Style

colorama.init()

DB_USER = config("user")
DB_PASS = config("password")
DB_NAME = config("name")
DB_HOST = config("host")
DB_PORT = config("port")


################################################################################
# Connect to MySQL database
################################################################################


def connect_to_db():
    try:
        cnx = mysql.connector.connect(
            user=DB_USER, password=DB_PASS, host=DB_HOST, database=DB_NAME, port=DB_PORT
        )
        print(f"{Fore.GREEN}DB_STATUS: Connection established {Style.RESET_ALL}")
        return cnx
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print(
                f"{Fore.RED}ERROR: Something is wrong with your user name or password {Style.RESET_ALL}"
            )
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print(f"{Fore.RED}ERROR: Database does not exist {Style.RESET_ALL}")
        else:
            print(err)
