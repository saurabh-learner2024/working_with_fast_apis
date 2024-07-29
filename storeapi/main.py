import logging
from contextlib import asynccontextmanager
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler
from storeapi.database import database
from storeapi.logging_conf import configure_logging
from storeapi.routers.post import router as post_router
from storeapi.routers.user import router as user_router
from storeapi.routers.upload import router as upload_router


logger = logging.getLogger(__name__)


# A context manager is basically a function that does some setup and some teardown. And in middle it pauses execution
# until something happens
@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)
app.add_middleware(CorrelationIdMiddleware)


# app.include_router(post_router, prefix="/posts")
app.include_router(post_router)
app.include_router(user_router)
app.include_router(upload_router)

@app.exception_handler(HTTPException)
async def http_exception_handle_logging(request, exc):
    logger.error(f"HTTPException: {exc.status_code} {exc.detail}")
    return await http_exception_handler(request, exc)
