import os
import psycopg2
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

# Get full database URL from env
db_url = os.getenv("DATABASE_URL")

if not db_url:
    raise Exception("DATABASE_URL environment variable is not set.")

# Parse the URL
result = urlparse(db_url)

# Extract components
DB_NAME = result.path[1:]           # removes leading '/'
DB_USER = result.username
DB_PASSWORD = result.password
DB_HOST = result.hostname
DB_PORT = result.port

# Connect to the database
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
)

conn.autocommit = True
cursor = conn.cursor()

# Check if the database already exists
cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
exists = cursor.fetchone()

# Create database if it doesnt exist
if not exists:
    cursor.execute(f'CREATE DATABASE "{DB_NAME}";')
    print(f"✅ Database '{DB_NAME}' created.")
else:
    print(f"ℹ️ Database '{DB_NAME}' already exists.")

cursor.close()
conn.close()
