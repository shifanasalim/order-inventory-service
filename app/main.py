from fastapi import FastAPI

app = FastAPI(
title="Order and Inventory Service",
description="API for managing products, inventory, and orders",
version="1.0.0",
)


@app.get("/")
async def home():
return {"message": "Order and Inventory Service is running"}


@app.get("/health")
async def health():
return {"status": "healthy"}
