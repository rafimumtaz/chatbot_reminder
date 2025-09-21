from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base # Import ini
from dotenv import load_dotenv
import os

load_dotenv()

# Mengambil kredensial dari file .env
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_NAME = os.getenv("DB_NAME", "chatbot_reminder")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "")

# Buat string koneksi database
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

# Buat engine dan SessionLocal
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Ini adalah kelas dasar deklaratif untuk model-model SQLAlchemy
Base = declarative_base()

def get_db():
    """
    Dependency untuk mendapatkan sesi database.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()