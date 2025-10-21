from sqlalchemy.orm import Session
from src.database.session import get_db_session
from fastapi import Depends
from src.repositories.user_repository import *

def get_user_repository(db: Session = Depends(get_db_session)) -> UserRepository:
    return UserRepository(db=db)
