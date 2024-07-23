from fastapi import FastAPI
from storeapi.routers.post import router as post_router

app = FastAPI()

# app.include_router(post_router, prefix="/posts")
app.include_router(post_router)