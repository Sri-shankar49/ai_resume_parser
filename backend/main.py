import os

from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.routers.resume_router import router as resume_router
from src.services.resume_repository import initialize_database

from src.utils.error_utils import AppError, log_internal_error
from fastapi.responses import JSONResponse

from fastapi import Request
from fastapi.responses import JSONResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield
    
app = FastAPI(
    title="AI Resume Parser API",
    description="An AI-powered resume parsing application",
    version="1.0.0",
    lifespan=lifespan,
)

cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173",
    ).split(",")
    if origin.strip()
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "message": "AI Resume Parser API is running!"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
    
app.include_router(resume_router)   

@app.exception_handler(AppError)
async def app_error_handler(
    request: Request,
    exc: AppError,
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.message,
            }
        },
    )


@app.exception_handler(Exception)
async def unexpected_error_handler(
    request: Request,
    exc: Exception,
):
    log_internal_error(
        f"{request.method} {request.url.path}",
        exc,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "message": "An unexpected server error occurred."
            }
        },
    )





@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.message,
            }
        },
    )


@app.exception_handler(Exception)
async def unexpected_error_handler(
    request: Request,
    exc: Exception,
):
    log_internal_error(
        f"{request.method} {request.url.path}",
        exc,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "message": "An unexpected server error occurred."
            }
        },
    )
 