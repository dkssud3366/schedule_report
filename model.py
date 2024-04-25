import mysql.connector
from datetime import datetime,timedelta 
import os


today = datetime.now().date()
yesterday = today - timedelta(days=1)
month = today.month

def get_conn():
    return mysql.connector.connect(
        host= os.getenv('host'),
        user=os.getenv('user'),
        password=os.getenv('password'),
        database=os.getenv('database'),
        charset='utf8'
    )

def query_db(sql, values=None):
    try:
        with get_conn() as conn:
            cursor = conn.cursor(dictionary=True)
            if values is not None:
                cursor.execute(sql, values)
            else:
                cursor.execute(sql)
            result = cursor.fetchall()
            return result
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        raise  






