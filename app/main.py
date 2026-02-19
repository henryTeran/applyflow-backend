"""
ApplyFlow API - Main application entry point.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.config import settings
from app.api import api_router
from app.logging_config import LoggingMiddleware, get_logger
from app.rate_limiting import limiter

# Initialize logger
logger = get_logger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
# ApplyFlow API - Personal ATS + CRM for Job Applications

**ApplyFlow** helps you manage your job search efficiently by:
- 📝 Storing and tracking job offers
- 🎯 Computing match scores between you and job requirements
- ✍️ Generating tailored cover letters and PDFs
- 📧 Managing applications and email communications
- 📊 Tracking your application pipeline with timeline events
- 🤖 Optional AI-powered features using OpenAI GPT

## Features

### 🔐 Authentication
- JWT-based authentication
- Secure password hashing with bcrypt
- Token refresh mechanism

### 💼 Job Management
- Create and track job offers
- Compute compatibility scores
- AI-powered job analysis
- Automatic draft generation

### 📄 Documents
- Upload CV/resume
- Generate cover letters
- Create PDFs from templates
- Manage application documents

### 📧 Email & Communication
- Send applications via SMTP
- Background email queue (Celery)
- Email templates

### 🔔 Webhooks
- Receive updates from job portals
- Automatic status updates
- Interview scheduling notifications

### 📈 Application Tracking
- CRM-style application management
- Timeline events
- Status tracking
- Notes and follow-ups

## Getting Started

1. **Register**: POST `/api/v1/auth/register`
2. **Login**: POST `/api/v1/auth/login`
3. **Create Job Offer**: POST `/api/v1/job-offers/`
4. **Run Pipeline**: POST `/api/v1/job-offers/{id}/run-pipeline`
5. **Review Draft**: GET `/api/v1/drafts/`
6. **Submit Application**: POST `/api/v1/applications/`

## Documentation

- **Interactive Docs**: [/docs](/docs)
- **Alternative Docs**: [/redoc](/redoc)
- **GitHub**: Coming soon

## Support

For questions or issues, please contact support.
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=[
        {
            "name": "authentication",
            "description": "User registration, login, and token management"
        },
        {
            "name": "job-offers",
            "description": "Manage job offers and run matching pipeline"
        },
        {
            "name": "job-matches",
            "description": "View and manage job match scores"
        },
        {
            "name": "drafts",
            "description": "Application drafts with cover letters and emails"
        },
        {
            "name": "applications",
            "description": "Track submitted applications and their status"
        },
        {
            "name": "timeline",
            "description": "Timeline events for application tracking"
        },
        {
            "name": "users",
            "description": "User management"
        },
        {
            "name": "uploads",
            "description": "File uploads for CV, documents, etc."
        },
        {
            "name": "webhooks",
            "description": "Receive updates from external job portals"
        }
    ]
)

# Setup rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    if not settings.debug:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# Configure CORS
allowed_origins = [
    "http://localhost:3000",  # React/Next.js dev
    "http://localhost:5173",  # Vite dev server (port par défaut)
    "http://localhost:5174",  # Vite dev server (port alternatif)
    "http://localhost:8000",  # API docs
]
# En production, ajouter les vrais domaines
if not settings.debug:
    # allowed_origins = ["https://applyflow.com", "https://www.applyflow.com"]
    pass

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Exception handlers
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle SQLAlchemy database errors."""
    logger.error("database_error", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "A database error occurred. Please try again later."}
    )

@app.exception_handler(IntegrityError)
async def integrity_exception_handler(request: Request, exc: IntegrityError):
    """Handle database integrity constraint violations."""
    logger.warning("integrity_error", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Resource conflict. This item may already exist."}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    logger.error("unhandled_exception", 
                error=str(exc), 
                exc_type=type(exc).__name__,
                path=request.url.path)
    
    # Ne pas révéler les détails en production
    detail = str(exc) if settings.debug else "An internal error occurred"
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": detail}
    )

logger.info("application_started", version=settings.app_version, debug=settings.debug)


@app.get("/")
@limiter.limit("100/minute")
def root(request: Request):
    """Root endpoint."""
    return {
        "message": "Welcome to ApplyFlow API",
        "version": settings.app_version,
        "docs": "/docs"
    }


@app.get("/ping")
@limiter.limit("200/minute")
def ping(request: Request):
    """Health check endpoint."""
    return {"status": "ok", "message": "pong"}


@app.get("/health")
@limiter.limit("100/minute")
def health(request: Request):
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "debug": settings.debug
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
