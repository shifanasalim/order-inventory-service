from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


# -------------------------
# Product schemas
# -------------------------

class ProductCreate(BaseModel):
    """Fields required to create a product."""

    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    stock_quantity: int = Field(ge=0)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Product name cannot be empty.")
        return value


class ProductUpdate(BaseModel):
    """Fields that can be updated on a product."""

    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    price: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=12,
        decimal_places=2,
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip()
        if not value:
            raise ValueError("Product name cannot be empty.")
        return value


class ProductResponse(BaseModel):
    """Product data returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    price: Decimal
    stock_quantity: int
    created_at: datetime
    updated_at: datetime


class StockUpdate(BaseModel):
    """Request to set the current stock quantity."""

    stock_quantity: int = Field(ge=0)


# -------------------------
# Order schemas
# -------------------------

class OrderItemCreate(BaseModel):
    """One product requested in an order."""

    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    """Request to place an order containing one or more items."""

    items: list[OrderItemCreate] = Field(min_length=1, max_length=100)


class OrderItemResponse(BaseModel):
    """One item in a completed or pending order."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    quantity: int
    unit_price: Decimal


class OrderResponse(BaseModel):
    """Order details returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    total_price: Decimal
    created_at: datetime
    items: list[OrderItemResponse]


# -------------------------
# Pagination schemas
# -------------------------

class ProductListResponse(BaseModel):
    """Paginated product results."""

    items: list[ProductResponse]
    total: int
    limit: int
    offset: int


class OrderListResponse(BaseModel):
    """Paginated order results."""

    items: list[OrderResponse]
    total: int
    limit: int
    offset: int