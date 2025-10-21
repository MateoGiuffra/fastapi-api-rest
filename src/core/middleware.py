from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse
from jose import JWTError
from src.schemas.error import ErrorDTO
from src.services.cookie_service import CookieService

PUBLIC_ENDPOINTS = ["/", "/docs", "/openapi.json"]

class Middleware(BaseHTTPMiddleware):
    def __init__(self, app, dispatch = None):
        super().__init__(app, dispatch)
        self.cookie_service = CookieService()
    
    async def dispatch(self, request: Request, call_next: callable):
        if request.url.path in PUBLIC_ENDPOINTS or request.url.path.startswith("/auth"):
            return await call_next(request)


        errorDTO = ErrorDTO(
            status_code=401,
            message="Unauthorized: No token provided",
            detail=[]
        ).model_dump()
        
        token = self.cookie_service.get_token(request)

        if not token:
            return JSONResponse(
                status_code=401,
                content=errorDTO
            )

        try:
            self.cookie_service.validate_token(token)
            response = await call_next(request)
            return response
        except JWTError:
            return JSONResponse(
                status_code=401,
                content=errorDTO
            )
        except Exception as e:
            print("Exception middleware: ", e, "type: ", type(e))
            return JSONResponse(
                status_code=401,
                content=ErrorDTO(
                    status_code=500,
                    message="Something went wrong. Try again later.",
                    detail=[]
                ).model_dump()
        )
    
