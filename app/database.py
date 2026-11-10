import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="ecommerce_feedback_db",
        user="postgres",
        password="postgresuzyy",
        port="5432",
        cursor_factory=RealDictCursor
    )