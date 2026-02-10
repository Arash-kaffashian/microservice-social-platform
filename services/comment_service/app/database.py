from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from decouple import config


# database configuration
DB_USER = config("POSTGRES_USER")
DB_PASSWORD = config("POSTGRES_PASSWORD")
DB_HOST = config("POSTGRES_HOST")
DB_PORT = config("POSTGRES_PORT", cast=int)
DB_NAME = config("POSTGRES_DB")

# SQLAlchemy to Postgresql pathing
SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SQLAlchemy configuration
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# FastAPI dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
