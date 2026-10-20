from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="OpenData Warehouse API",
    description="Analytics API for GitHub repository data",
    version="1.0.0",
)

app.include_router(router)