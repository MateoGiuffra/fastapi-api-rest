from pydantic import BaseModel, Field
from fastapi import Query

class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=25, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit

def get_pagination_params(
    page: int = Query(1, ge=1, description="Page number"), 
    limit: int = Query(25, le=100, description="Elements per page")
) -> PaginationParams:
    return PaginationParams(page=page, limit=limit)

class PaginationResponse(BaseModel):
    model_config = {"from_attributes": True}

    list: list
    page: int
    limit: int
    total_pages: int
    total_entities: int