"""
API v1 initialization.
"""

from fastapi import APIRouter
from app.api.v1 import job_offers, job_matches, drafts, applications, timeline, users, auth, uploads, webhooks, health

# Create main API v1 router
api_router = APIRouter()

# Health check endpoints (no auth required)
api_router.include_router(
    health.router,
    tags=["health"]
)

# Authentication endpoints (no prefix)
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"]
)

# File upload endpoints
api_router.include_router(
    uploads.router,
    prefix="/uploads",
    tags=["uploads"]
)

# Webhook endpoints
api_router.include_router(
    webhooks.router,
    prefix="/webhooks",
    tags=["webhooks"]
)

# Include all sub-routers
api_router.include_router(
    job_offers.router,
    prefix="/job-offers",
    tags=["job-offers"]
)

api_router.include_router(
    job_matches.router,
    prefix="/job-matches",
    tags=["job-matches"]
)

api_router.include_router(
    drafts.router,
    prefix="/drafts",
    tags=["drafts"]
)

api_router.include_router(
    applications.router,
    prefix="/applications",
    tags=["applications"]
)

api_router.include_router(
    timeline.router,
    prefix="/timeline",
    tags=["timeline"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)
