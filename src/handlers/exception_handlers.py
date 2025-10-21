from fastapi import Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from src.utils.fast_api_args import get_json
from src.schemas.error import ErrorDTO

class HandlerException:
    """
    Class that returns a JSON response standardized with the error details in every method.
    """
    
    async def validation_exception_handler(self, request: Request, exc: RequestValidationError):
        """
        Validations errors Pydantic manager.
        """ 
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        errors = exc.errors()
        return JSONResponse(
            status_code=status_code,
            content=ErrorDTO(status_code=status_code, message=errors[0]['msg'], detail=[error["msg"] for error in errors]).model_dump(),
        )
    
    async def http_fast_api_exception(self, request: Request, exc: HTTPException):
        """
        Http fast api exceptions manager.
        """
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorDTO(status_code=exc.status_code, message=exc.detail).model_dump(),
        )
        
    # async def business_exception_handler(self, request: Request, exc: BusinessException):
    #     """
    #     Manejador para nuestras excepciones de negocio personalizadas (BusinessException).
    #     Devuelve una respuesta JSON estandarizada usando ErrorDTO.
    #     """
    #     return JSONResponse(
    #         status_code=exc.status_code,
    #         content=ErrorDTO(status_code=exc.status_code, message=exc.message).model_dump(),
    #     )

handler_instance = HandlerException()
exception_handlers = get_json(handler_instance)
