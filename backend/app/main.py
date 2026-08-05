from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.auth import router as auth_router
from app.core.config import settings

# Initialize FastAPI app instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS Middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include Authentication Routes
app.include_router(auth_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health Check"])
def health_check():
    """Simple status check to verify server health."""
    return {
        "status": "healthy",
        "app_name": settings.PROJECT_NAME,
    }


@app.get("/", tags=["Root"])
def root():
    return {"message": f"Welcome to the {settings.PROJECT_NAME} API"}