from fastapi import FastAPI
from src.routers import routers
from src.handlers import exception_handlers
from src.core.middleware import Middleware as CustomMiddleware
from src.core.config import register_public_endpoint

app = FastAPI(
    description="API REST",
    version="1.0.1",
    exception_handlers=exception_handlers
)

app.add_middleware(CustomMiddleware)
for router in routers:
    app.include_router(router)

register_public_endpoint(app)