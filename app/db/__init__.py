import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "5432")

# Connect to database
conn = psycopg2.connect(dbname="postgres", user=db_user, host=db_host, port=db_port)
conn.autocommit = True
cursor = conn.cursor()

# Check if the database already exists
cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
exists = cursor.fetchone()

# Create database if it doesnt exist
if not exists:
    cursor.execute(f'CREATE DATABASE "{db_name}";')
    print(f"✅ Database '{db_name}' created.")
else:
    print(f"ℹ️ Database '{db_name}' already exists.")

cursor.close()
conn.close()
