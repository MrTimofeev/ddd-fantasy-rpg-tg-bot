from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base

def get_seesion_local(db_path: str = "sqlite:///game.db"):
    engine = create_engine(db_path, connect_args={"check_same_thered": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommint=False, autoflush=False, bind=engine)
    return SessionLocal
    