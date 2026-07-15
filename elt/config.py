import os

from dotenv import load_dotenv

load_dotenv()

# API
API_KEY = os.getenv("API_KEY")
COMPETITION_CODE = os.getenv("COMPETITION_CODE")

# PostgreSQL
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_HOST = os.getenv("DB_HOST")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Connection string
DB_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
