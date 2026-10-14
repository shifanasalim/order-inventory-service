from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Product
from app.schemas import (
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
    StockUpdate,
)

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/",response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,)

async def create_product(product_data: ProductCreate,db: AsyncSession = Depends(get_db),):
    product = Product(**product_data.model_dump())

    db.add(product)
    await db.commit()
    await db.refresh(product)

    return product


@router.get("/", response_model=ProductListResponse)
async def list_products(limit: int = Query(default=20, ge=1, le=100),offset: int = Query(default=0, ge=0),db: AsyncSession = Depends(get_db),):
    total_result = await db.execute(select(func.count()).select_from(Product))
    total = total_result.scalar_one()

    result = await db.execute(select(Product).order_by(Product.id).limit(limit).offset(offset))
    products = result.scalars().all()

    return {
        "items": products,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db),):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Product not found",)

    return product


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int,product_data: ProductUpdate,db: AsyncSession = Depends(get_db),):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Product not found",)

    changes = product_data.model_dump(exclude_unset=True)

    for field, value in changes.items():
        setattr(product, field, value)

    await db.commit()
    await db.refresh(product)

    return product


@router.patch( "/{product_id}/stock",response_model=ProductResponse,)
async def update_stock(product_id: int,stock_data: StockUpdate,db: AsyncSession = Depends(get_db),):

    result = await db.execute(update(Product).where(Product.id == product_id).values(stock_quantity=stock_data.stock_quantity).returning(Product.id))

    updated_id = result.scalar_one_or_none()

    if updated_id is None:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Product not found",)

    await db.commit()

    result = await db.execute(select(Product).where(Product.id == product_id))
    return result.scalar_one()