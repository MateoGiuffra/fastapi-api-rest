from src.routers.auth_router import router as auth_router
from src.routers.user_router import router as user_router

routers = [
    auth_router,
    user_router
]
