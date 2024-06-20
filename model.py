import mysql.connector

import os

def get_conn():
    return mysql.connector.connect(
        host= os.getenv('HOST'),
        user=os.getenv('USER'),
        password=os.getenv('PASSWORD'),
        database=os.getenv('DATABASE'),
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





