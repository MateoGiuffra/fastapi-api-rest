from starlette.middleware.base import BaseHTTPMiddleware
from src.services.cookie_service import CookieService
from src.core.config import PUBLIC_ENDPOINTS
from fastapi.responses import JSONResponse
from src.schemas.error import ErrorDTO
from fastapi import Request
from jose import JWTError

class Middleware(BaseHTTPMiddleware):
    def __init__(self, app, dispatch = None):
        super().__init__(app, dispatch)
        self.cookie_service = CookieService()
    
    async def dispatch(self, request: Request, call_next: callable):
        if request.url.path in PUBLIC_ENDPOINTS:
            return await call_next(request)
        
        token = self.cookie_service.get_token(request)

        try:
            self.cookie_service.validate_token(token)
            return await call_next(request)
        except JWTError:
            return JSONResponse(
                status_code=401,
                content=ErrorDTO(
                        status_code=401,
                        message="Unauthorized: No token provided",
                        detail=[]
                    ).model_dump()
            )
        except Exception as e:
            print("Exception middleware: ", e, "type: ", type(e))
            return JSONResponse(
                status_code=500,
                content=ErrorDTO(
                    status_code=500,
                    message="Something went wrong. Try again later.",
                    detail=[]
                ).model_dump()
        )
    
