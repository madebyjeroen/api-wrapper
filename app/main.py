from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.router import router

app = FastAPI(openapi_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
)

app.include_router(router)
