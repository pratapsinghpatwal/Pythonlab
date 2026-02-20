# db_config.py

import psycopg2

def connect():
    return psycopg2.connect(
        dbname="testdb",
        user="postgres",
        password="1234",
        host="localhost",
        port="5432"
    )
