# Development Commands Cheatsheet

## Setup

### Initial setup
```bash
# Copy environment file
cp .env.example .env

# Edit .env with your settings
# Update DATABASE_URL, SMTP settings, etc.

# Run setup script
python setup.py
```

### Manual setup
```bash
# Install dependencies
pip install -r requirements.txt

# Create database (PostgreSQL must be running)
createdb applyflow_db

# Generate and apply migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

# Seed sample data
python seed_data.py
```

## Running the Server

### Development mode (with auto-reload)
```bash
uvicorn app.main:app --reload
```

### Production mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### With custom port
```bash
uvicorn app.main:app --reload --port 8080
```

## Database Migrations

### Create new migration
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply all pending migrations
```bash
alembic upgrade head
```

### Rollback last migration
```bash
alembic downgrade -1
```

### View migration history
```bash
alembic history
```

### Rollback to specific revision
```bash
alembic downgrade <revision_id>
```

### Check current revision
```bash
alembic current
```

## Database Management

### PostgreSQL commands
```bash
# Create database
createdb applyflow_db

# Drop database
dropdb applyflow_db

# Connect to database
psql applyflow_db

# Dump database
pg_dump applyflow_db > backup.sql

# Restore database
psql applyflow_db < backup.sql
```

### Inside psql
```sql
-- List tables
\dt

-- Describe table
\d job_offers

-- Show all databases
\l

-- Quit
\q
```

## API Testing

### Using curl

#### Create a job offer
```bash
curl -X POST http://localhost:8000/api/v1/job-offers/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Python Developer",
    "company": "TechCorp",
    "location": "Geneva",
    "source": "LinkedIn",
    "application_type": "email",
    "raw_description": "Looking for Python developer..."
  }'
```

#### List job offers
```bash
curl http://localhost:8000/api/v1/job-offers/
```

#### Get specific job offer
```bash
curl http://localhost:8000/api/v1/job-offers/1
```

#### Run pipeline on a job
```bash
curl -X POST http://localhost:8000/api/v1/job-offers/1/run-pipeline
```

#### List matches
```bash
curl http://localhost:8000/api/v1/job-matches/
```

#### List matches with minimum score
```bash
curl http://localhost:8000/api/v1/job-matches/?min_score=70
```

#### Create application
```bash
curl -X POST http://localhost:8000/api/v1/applications/ \
  -H "Content-Type: application/json" \
  -d '{
    "job_offer_id": 1,
    "channel": "email",
    "submitted_by": "manual",
    "status": "sent"
  }'
```

#### Update application status
```bash
curl -X PATCH http://localhost:8000/api/v1/applications/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "interview"}'
```

#### Add timeline event
```bash
curl -X POST http://localhost:8000/api/v1/timeline/application/1 \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": 1,
    "event_type": "interview",
    "description": "Phone interview scheduled",
    "event_date": "2025-12-05T14:00:00Z"
  }'
```

### Using httpie (if installed)
```bash
# Install httpie
pip install httpie

# Create job offer
http POST localhost:8000/api/v1/job-offers/ \
  title="Senior Python Developer" \
  company="TechCorp" \
  location="Geneva" \
  source="LinkedIn" \
  application_type="email" \
  raw_description="Looking for Python developer..."

# List job offers
http GET localhost:8000/api/v1/job-offers/

# Run pipeline
http POST localhost:8000/api/v1/job-offers/1/run-pipeline
```

## Python Shell

### Interactive shell with models
```bash
python
```

```python
from app.database import SessionLocal
from app.models import JobOffer, JobMatch, Application
from app.crud import job_offer as job_offer_crud

db = SessionLocal()

# Query jobs
jobs = db.query(JobOffer).all()
for job in jobs:
    print(f"{job.id}: {job.title} at {job.company}")

# Get a specific job
job = job_offer_crud.get(db, 1)
print(job.title)

# Close session
db.close()
```

## Code Quality

### Format code with black
```bash
pip install black
black app/
```

### Sort imports
```bash
pip install isort
isort app/
```

### Type checking
```bash
pip install mypy
mypy app/
```

### Linting
```bash
pip install flake8
flake8 app/
```

### All at once
```bash
black app/ && isort app/ && flake8 app/
```

## Testing (when tests are added)

### Run all tests
```bash
pytest
```

### Run specific test file
```bash
pytest tests/test_job_offers.py
```

### Run with coverage
```bash
pytest --cov=app --cov-report=html
```

## Docker (when Dockerfile is added)

### Build image
```bash
docker build -t applyflow-backend .
```

### Run container
```bash
docker run -p 8000:8000 --env-file .env applyflow-backend
```

### Docker Compose
```bash
docker-compose up -d
```

## Useful Queries

### Count records
```python
from app.database import SessionLocal
from app.models import JobOffer, JobMatch, Application

db = SessionLocal()

print(f"Job Offers: {db.query(JobOffer).count()}")
print(f"Matches: {db.query(JobMatch).count()}")
print(f"Applications: {db.query(Application).count()}")

db.close()
```

### Get high-scoring matches
```python
from app.database import SessionLocal
from app.models import JobMatch

db = SessionLocal()

high_matches = db.query(JobMatch).filter(JobMatch.score >= 70).all()
for match in high_matches:
    print(f"Match {match.id}: Score {match.score}")

db.close()
```

## Environment Variables Reference

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=your-email@gmail.com
SMTP_USE_TLS=True

# OpenAI
OPENAI_API_KEY=sk-your-key

# Application
APP_NAME=ApplyFlow API
APP_VERSION=1.0.0
DEBUG=True

# File Storage
GENERATED_DOCS_PATH=./generated_docs
```

## Troubleshooting

### Port already in use
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

### Database connection errors
- Check if PostgreSQL is running
- Verify DATABASE_URL in .env
- Check database exists: `psql -l`
- Check user permissions

### Import errors
- Activate virtual environment
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (need 3.10+)

### Alembic errors
- Check DATABASE_URL is correct
- Ensure all models are imported in alembic/env.py
- Delete alembic/versions/*.py and regenerate if needed

## Quick Reference URLs

- API Documentation: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json
- Health Check: http://localhost:8000/ping
