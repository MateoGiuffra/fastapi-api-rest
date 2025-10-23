from fastapi import FastAPI
from src.routers import routers
from fastapi.routing import APIRoute
from src.handlers import exception_handlers
from src.core.middleware import JWTCookieAuthMiddleware
from src.core.config import settings

app = FastAPI(
    description="API REST",
    version="1.0.1",
    exception_handlers=exception_handlers
)

def set_up():
    public_paths = set(settings.DEFAULT_PUBLIC_PATHS)
    for router in routers:
        app.include_router(router)
    for route in app.routes:
        if isinstance(route, APIRoute):
            if getattr(route.endpoint, "_is_public", False):
                public_paths.add(route.path)
    
    app.add_middleware(JWTCookieAuthMiddleware, public_paths=public_paths)


set_up()