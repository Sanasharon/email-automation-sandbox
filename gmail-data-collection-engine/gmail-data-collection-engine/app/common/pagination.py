from typing import Generic, TypeVar, List, Any
from pydantic import BaseModel
from fastapi import Query
from sqlalchemy.orm import Query as SAQuery

DataT = TypeVar("DataT")

class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool

class PaginatedResponse(BaseModel, Generic[DataT]):
    data: List[DataT]
    meta: PaginationMeta

def get_pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page")
):
    return {"page": page, "page_size": page_size}

def paginate_query(query: SAQuery, page: int, page_size: int) -> tuple[List[Any], PaginationMeta]:
    """Applies pagination to an SQLAlchemy query and returns results with metadata."""
    total_items = query.count()
    total_pages = (total_items + page_size - 1) // page_size
    
    skip = (page - 1) * page_size
    items = query.offset(skip).limit(page_size).all()
    
    meta = PaginationMeta(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1
    )
    return items, meta
