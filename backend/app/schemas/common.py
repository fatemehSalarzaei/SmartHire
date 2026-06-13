from math import ceil
from typing import Any

from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=25, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool
    has_previous: bool

    @classmethod
    def from_params(cls, params: PaginationParams, *, total: int) -> "PaginationMeta":
        total_pages = ceil(total / params.page_size) if total else 0
        return cls(
            page=params.page,
            page_size=params.page_size,
            total=total,
            total_pages=total_pages,
            has_next=params.page < total_pages,
            has_previous=params.page > 1 and total_pages > 0,
        )


def paginated_response(data: list[dict[str, Any]], meta: PaginationMeta) -> dict[str, Any]:
    return {
        "success": True,
        "data": data,
        "pagination": meta.model_dump(),
    }
