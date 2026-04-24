from fastapi import FastAPI
from api.chat import router

app = FastAPI(title="Recipe Generator")

app.include_router(router, prefix="/api", tags=["chat"])