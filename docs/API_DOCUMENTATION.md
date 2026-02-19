# 📚 API Documentation Guide

## Overview

ApplyFlow provides a comprehensive REST API for managing your job application workflow. This guide covers all endpoints, authentication, and usage examples.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All endpoints (except `/auth/register` and `/auth/login`) require JWT authentication.

### Register

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2025-12-01T10:00:00Z"
}
```

### Login

```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=securepassword123
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using the Token

Include the token in the Authorization header:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 💼 Job Offers

### Create Job Offer

```http
POST /api/v1/job-offers/
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Senior Python Developer",
  "company": "TechCorp",
  "location": "Geneva, Switzerland",
  "source": "LinkedIn",
  "url": "https://linkedin.com/jobs/123456",
  "application_type": "email",
  "raw_description": "We are looking for a Senior Python Developer with 5+ years experience in FastAPI, PostgreSQL, and REST APIs. You will work on building scalable backend services..."
}
```

### List Job Offers

```http
GET /api/v1/job-offers/?skip=0&limit=10
Authorization: Bearer {token}
```

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Max records to return (default: 100)

### Get Job Offer

```http
GET /api/v1/job-offers/{id}
Authorization: Bearer {token}
```

### Update Job Offer

```http
PATCH /api/v1/job-offers/{id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Senior Python Developer (Updated)",
  "status": "applied"
}
```

### Delete Job Offer

```http
DELETE /api/v1/job-offers/{id}
Authorization: Bearer {token}
```

### Run Complete Pipeline

Computes match score, generates cover letter, and creates draft:

```http
POST /api/v1/job-offers/{id}/run-pipeline
Authorization: Bearer {token}
```

**Response:**
```json
{
  "job_offer": {...},
  "match": {
    "id": 1,
    "score": 85.5,
    "reason": "Strong match based on skills and experience"
  },
  "draft": {
    "id": 1,
    "cover_letter_text": "Dear Hiring Manager...",
    "cover_letter_path": "/generated_docs/cover_letter_123.pdf",
    "email_subject": "Application for Senior Python Developer",
    "email_body": "..."
  }
}
```

## 🎯 Job Matches

### List Matches

```http
GET /api/v1/job-matches/?min_score=70&limit=10
Authorization: Bearer {token}
```

**Query Parameters:**
- `min_score`: Minimum match score (0-100)
- `job_offer_id`: Filter by job offer
- `skip`, `limit`: Pagination

### Get Match

```http
GET /api/v1/job-matches/{id}
Authorization: Bearer {token}
```

## 📄 Application Drafts

### List Drafts

```http
GET /api/v1/drafts/?skip=0&limit=10
Authorization: Bearer {token}
```

### Get Draft

```http
GET /api/v1/drafts/{id}
Authorization: Bearer {token}
```

### Update Draft

Edit the generated draft before sending:

```http
PATCH /api/v1/drafts/{id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "cover_letter_text": "Edited cover letter...",
  "email_body": "Edited email body..."
}
```

## 📧 Applications

### Create Application

After reviewing and approving a draft:

```http
POST /api/v1/applications/
Authorization: Bearer {token}
Content-Type: application/json

{
  "job_offer_id": 1,
  "channel": "email",
  "submitted_by": "manual",
  "status": "sent",
  "sent_at": "2025-12-01T14:30:00Z"
}
```

**Channels:** `email`, `portal`, `recruiter`, `direct`, `other`
**Statuses:** `draft`, `sent`, `viewed`, `interview`, `rejected`, `offer`, `accepted`, `declined`

### List Applications

```http
GET /api/v1/applications/?status=sent&limit=10
Authorization: Bearer {token}
```

**Query Parameters:**
- `status`: Filter by status
- `channel`: Filter by channel
- `job_offer_id`: Filter by job offer

### Get Application

```http
GET /api/v1/applications/{id}
Authorization: Bearer {token}
```

### Update Application Status

```http
PATCH /api/v1/applications/{id}/status
Authorization: Bearer {token}
Content-Type: application/json

{
  "status": "interview"
}
```

## 📊 Timeline Events

### List Events for Application

```http
GET /api/v1/timeline/application/{application_id}
Authorization: Bearer {token}
```

### Create Event

```http
POST /api/v1/timeline/application/{application_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "event_type": "note",
  "title": "Follow-up call scheduled",
  "description": "Spoke with recruiter, technical interview next week"
}
```

**Event Types:** `status_change`, `interview`, `note`, `email_sent`, `email_received`, `offer_received`, `other`

## 📎 File Uploads

### Upload CV

```http
POST /api/v1/uploads/upload/cv
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: [CV.pdf]
```

**Accepted formats:** PDF, DOC, DOCX, TXT, RTF
**Max size:** 10MB

### Upload Document

```http
POST /api/v1/uploads/upload/document
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: [document.pdf]
```

### List Uploaded Files

```http
GET /api/v1/uploads/files/list?category=cv
Authorization: Bearer {token}
```

### Download File

```http
GET /api/v1/uploads/files/download/{category}/{filename}
Authorization: Bearer {token}
```

### Delete File

```http
DELETE /api/v1/uploads/files/delete/{category}/{filename}
Authorization: Bearer {token}
```

## 🔔 Webhooks

### Application Update Webhook

Receive updates from job portals:

```http
POST /api/v1/webhooks/webhook/application-update
Content-Type: application/json
X-Webhook-Signature: {hmac_signature}

{
  "event_type": "status_update",
  "application_id": 1,
  "data": {
    "status": "interview",
    "message": "Interview scheduled for next week"
  },
  "timestamp": "2025-12-01T15:00:00Z"
}
```

**Event Types:**
- `status_update`: Application status changed
- `interview_scheduled`: Interview scheduled
- `rejection`: Application rejected
- `offer`: Job offer received

### Test Webhook

```http
POST /api/v1/webhooks/webhook/test
Content-Type: application/json

{
  "test": "data"
}
```

## 🔧 Advanced Features

### Background Task Processing (Celery)

Send emails asynchronously:

```python
from app.tasks.email_tasks import send_email_task

send_email_task.delay(
    to_email="hr@company.com",
    subject="Application for Senior Developer",
    body_html="<p>Dear Hiring Manager...</p>"
)
```

### AI-Powered Features

Enable by setting `OPENAI_API_KEY` in `.env`:

```python
from app.services.ai_service import ai_service

# AI match analysis
analysis = ai_service.generate_match_analysis(job_offer, candidate_profile)

# AI cover letter
cover_letter = ai_service.generate_cover_letter(job_offer, candidate_profile)

# Extract job details
details = ai_service.extract_job_details(raw_description)
```

### Rate Limiting

Default limits:
- General endpoints: 60 requests/minute
- Health checks: 200 requests/minute
- Auth endpoints: 10 requests/minute

Rate limits are per IP address.

## 📊 Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized (invalid/missing token) |
| 403 | Forbidden |
| 404 | Not Found |
| 413 | Payload Too Large |
| 422 | Validation Error |
| 429 | Too Many Requests (rate limit) |
| 500 | Internal Server Error |

## 🧪 Testing with curl

### Complete workflow example

```bash
# 1. Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","name":"Test User","password":"test123"}'

# 2. Login
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=test@example.com&password=test123" \
  | jq -r .access_token)

# 3. Create job offer
JOB_ID=$(curl -X POST http://localhost:8000/api/v1/job-offers/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Python Dev","company":"TechCo","location":"Remote","source":"LinkedIn","raw_description":"Looking for Python developer..."}' \
  | jq -r .id)

# 4. Run pipeline
curl -X POST "http://localhost:8000/api/v1/job-offers/$JOB_ID/run-pipeline" \
  -H "Authorization: Bearer $TOKEN"

# 5. List drafts
curl http://localhost:8000/api/v1/drafts/ \
  -H "Authorization: Bearer $TOKEN"
```

## 📚 Interactive Documentation

For interactive API testing, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🎯 Best Practices

1. **Always use HTTPS in production**
2. **Store tokens securely** (never in localStorage)
3. **Implement token refresh** before expiration
4. **Handle rate limits** gracefully
5. **Validate inputs** on client side
6. **Use pagination** for large datasets
7. **Log all API errors** for debugging

## 💡 Tips

- Use `?skip=0&limit=10` for pagination
- Filter results with query parameters
- Check response status codes
- Handle authentication errors
- Use webhooks for real-time updates

## 🔗 SDKs & Libraries

Python client example:

```python
import requests

class ApplyFlowClient:
    def __init__(self, base_url, email, password):
        self.base_url = base_url
        self.token = self._login(email, password)
    
    def _login(self, email, password):
        response = requests.post(
            f"{self.base_url}/auth/login",
            data={"username": email, "password": password}
        )
        return response.json()["access_token"]
    
    def _headers(self):
        return {"Authorization": f"Bearer {self.token}"}
    
    def create_job_offer(self, data):
        return requests.post(
            f"{self.base_url}/job-offers/",
            json=data,
            headers=self._headers()
        ).json()

# Usage
client = ApplyFlowClient("http://localhost:8000/api/v1", "user@example.com", "password")
job = client.create_job_offer({
    "title": "Python Developer",
    "company": "TechCorp",
    "location": "Remote",
    "source": "LinkedIn",
    "raw_description": "..."
})
```

## 📞 Support

For API support or questions:
- Check the interactive docs at `/docs`
- Review error messages in responses
- Check server logs for details

Happy job hunting! 🚀
