from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from constants import DATABASE

engine = create_engine(DATABASE.URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
