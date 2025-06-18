import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="sql12.freesqldatabase.com	",
        user="sql12785373",
        password="vmWujz8R5j",
        database="sql12785373"
    )
