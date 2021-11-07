
import os

# This is a bad place for this import
import pymysql

def get_db_info():
    """
    This is crappy code.

    :return: A dictionary with connect info for MySQL
    """
    db_host = os.environ.get("DBHOST", None)

    if db_host is None:

        db_info = {
            "host": "localhost",
            "user": "dbuser",
            "password": "dbuserdbuser",
            "cursorclass": pymysql.cursors.DictCursor
        }

    else:

        db_info = {
            "host": db_host,
            "user": os.environ.get("DBUSER"),
            "password": os.environ.get("DBPASSWORD"),
            "cursorclass": pymysql.cursors.DictCursor
        }

    return db_info

def get_sns_info():

    sns_access_key_id = os.environ.get("SNS_ACCESS_KEY_ID", None)
    sns_secret_key = os.environ.get("SNS_SECRET_KEY", None)
    topic_arn = os.environ.get("TOPIC_ARN", None)

    return sns_access_key_id, sns_secret_key, topic_arn

def get_google_info():

    google_id = os.environ.get("GOOGLE_ID", None)
    google_secret = os.environ.get("GOOGLE_SECRET", None)

    return google_id, google_secret
