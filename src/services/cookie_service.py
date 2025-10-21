from fastapi import Response
from jose import jwt
from src.database.models.user import User
from datetime import datetime, timedelta
from src.core.config import settings


class CookieService:
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.expiration_time = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.secure = settings.COOKIE_SECURE
        self.key = "token"
        
    def set_cookie(self, response: Response, user: User):
        token = self.create_token(user)
        response.set_cookie(
            key="token",
            value=token,
            httponly=True,
            samesite="lax", # 'strict' o 'lax' para protección CSRF
            secure=self.secure 
        )
    def clean_cookies(self, response: Response):
        response.delete_cookie(
            key=self.key,
            path="/"
        )
    
    def create_token(self, user: User) -> str:
        encode = {"sub": user.username, "id": user.id}
        expires = datetime.utcnow() + timedelta(minutes=self.expiration_time)
        encode.update({"exp": expires})
        return jwt.encode(
            encode,
            self.secret_key,
            algorithm=self.algorithm
        )
    
    def get_user_id_from_token(self, request: Response) -> str:
        token = request.cookies.get("token")
        if not token:
            return None
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload.get("id")
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def get_token(self, request: Response) -> str:
        return request.cookies.get(self.key)
    
    def validate_token(self, token: str):
        jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

       