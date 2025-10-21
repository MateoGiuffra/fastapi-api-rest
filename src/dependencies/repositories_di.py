from src.database.session import get_db_session
from src.repositories.user_repository import *
from sqlalchemy.orm import Session
from fastapi import Depends

def get_user_repository(db: Session = Depends(get_db_session)) -> UserRepository:
    return UserRepository(db=db)
