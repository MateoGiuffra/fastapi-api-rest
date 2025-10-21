from src.routers import *

router = APIRouter(prefix="/tests", tags=["tests"])

@public
@router.get("/register", status_code=status.HTTP_201_CREATED) 
async def register() -> str:
    return "hola"