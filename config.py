import os
from dotenv import load_dotenv

load_dotenv()


DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "business_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY") 