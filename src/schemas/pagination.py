from pydantic import BaseModel, Field
from fastapi import Query

class PaginationParams(BaseModel):
    page: int = Field(min=1, default=1)
    limit: int = Field(min=1, max=100, default=25)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit

def get_pagination_params(
    page: int = Query(1, ge=1, description="Número de página"), 
    limit: int = Query(25, le=100, description="Elementos por página")
) -> PaginationParams:
    return PaginationParams(page=page, limit=limit)

class PaginationResponse(BaseModel):
    model_config = {"from_attributes": True}

    list: list
    page: int
    limit: int
    total_pages: int
    total_entities: int