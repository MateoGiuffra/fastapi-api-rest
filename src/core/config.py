from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi import FastAPI
from fastapi.routing import APIRoute

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    COOKIE_SECURE: bool = False

settings = Settings()


PUBLIC_ENDPOINTS = set(["/", "/docs", "/openapi.json"])
def register_public_endpoint(app: FastAPI):
    for route in app.routes:
        if isinstance(route, APIRoute):
            if getattr(route.endpoint, "_is_public", False):
                PUBLIC_ENDPOINTS.add(route.path)