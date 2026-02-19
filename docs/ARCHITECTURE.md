# ApplyFlow Backend - Architecture Overview

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Future)                        │
│                     React / Vue / Next.js                        │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Application                         │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    API Layer (v1)                         │  │
│  │  • job_offers.py    • job_matches.py   • drafts.py       │  │
│  │  • applications.py  • timeline.py      • users.py        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   Agents Layer                            │  │
│  │  • pipeline_agent.py (orchestration)                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  Services Layer                           │  │
│  │  • match_service.py    (scoring logic)                    │  │
│  │  • draft_service.py    (PDF generation)                   │  │
│  │  • email_service.py    (SMTP)                             │  │
│  │  • ai_service.py       (OpenAI wrapper)                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    CRUD Layer                             │  │
│  │  • job_offer.py    • job_match.py   • application.py     │  │
│  │  • draft.py        • timeline.py    • user.py            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  SQLAlchemy ORM                           │  │
│  │  Models: User, JobOffer, JobMatch, ApplicationDraft,     │  │
│  │          Application, TimelineEvent                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │   PostgreSQL    │
                 │    Database     │
                 └─────────────────┘
```

## 📊 Data Model

```
┌──────────┐
│   User   │
└──────────┘
     │
     │ (Future: FK to applications)
     │
┌──────────────┐       ┌─────────────────┐       ┌──────────────────┐
│  JobOffer    │──────▶│   JobMatch      │       │                  │
│              │       │                 │       │  ApplicationDraft│
│ • title      │       │ • score         │◀──────│                  │
│ • company    │       │ • reasons       │       │ • cover_letter   │
│ • location   │       │ • skills_found  │       │ • pdf_path       │
│ • source     │       │ • red_flags     │       │ • email_subject  │
│ • raw_desc   │       └─────────────────┘       │ • email_body     │
└──────────────┘                                  └──────────────────┘
     │
     │
     ▼
┌──────────────┐       ┌─────────────────┐
│ Application  │──────▶│ TimelineEvent   │
│              │       │                 │
│ • channel    │       │ • event_type    │
│ • status     │       │ • description   │
│ • sent_at    │       │ • event_date    │
│ • reference  │       └─────────────────┘
└──────────────┘
```

### Relationships

- **JobOffer** → **JobMatch**: One-to-Many (can have multiple match attempts)
- **JobOffer** → **ApplicationDraft**: One-to-Many (can regenerate drafts)
- **JobOffer** → **Application**: One-to-Many (can apply multiple times)
- **Application** → **TimelineEvent**: One-to-Many (tracking all events)

## 🔄 Request Flow

### Example: Process a Job Offer

```
1. POST /api/v1/job-offers/
   └─▶ job_offers.create_job_offer()
       └─▶ crud.job_offer.create()
           └─▶ SQLAlchemy INSERT
               └─▶ PostgreSQL

2. POST /api/v1/job-offers/{id}/run-pipeline
   └─▶ job_offers.run_pipeline()
       └─▶ pipeline_agent.run_job_offer_pipeline()
           ├─▶ crud.job_offer.get()
           │   └─▶ Get JobOffer from DB
           │
           ├─▶ match_service.compute_match_score()
           │   ├─▶ Analyze job description
           │   ├─▶ Compare with candidate profile
           │   └─▶ Return MatchResult
           │
           ├─▶ crud.job_match.create()
           │   └─▶ Save JobMatch to DB
           │
           ├─▶ draft_service.create_application_draft()
           │   ├─▶ generate_cover_letter_text()
           │   ├─▶ generate_cover_letter_pdf()
           │   │   ├─▶ Jinja2.render()
           │   │   └─▶ WeasyPrint.write_pdf()
           │   ├─▶ generate_email_content()
           │   └─▶ crud.draft.create()
           │       └─▶ Save Draft to DB
           │
           └─▶ Return PipelineResult
               └─▶ JSON response with all data
```

## 🧩 Component Details

### API Layer (`app/api/v1/`)
- **Responsibility**: HTTP request/response handling
- **Validation**: Pydantic schemas for input/output
- **Dependencies**: Database session injection
- **Error Handling**: HTTPException for client errors

### Agents Layer (`app/agents/`)
- **Purpose**: Orchestrate complex multi-step workflows
- **Example**: `pipeline_agent.py` coordinates match + draft generation
- **Benefits**: Keeps controllers thin, business logic reusable

### Services Layer (`app/services/`)
- **match_service.py**: 
  - Rule-based job matching algorithm
  - Analyzes skills, location, seniority
  - Returns score (0-100) + reasons
  
- **draft_service.py**:
  - Cover letter text generation
  - PDF creation with WeasyPrint
  - Email draft preparation
  
- **email_service.py**:
  - SMTP configuration
  - Email sending with attachments
  - HTML and plain text support
  
- **ai_service.py**:
  - OpenAI API wrapper
  - Ready for custom prompts
  - Functions stubbed for future use

### CRUD Layer (`app/crud/`)
- **Responsibility**: Database operations only
- **No business logic**: Pure data access
- **Reusable**: Can be used from API, services, or scripts
- **Session management**: Receives `db: Session` parameter

### Models Layer (`app/models/`)
- **SQLAlchemy ORM models**
- **Database schema definition**
- **Relationships and indexes**
- **Used by Alembic for migrations**

### Schemas Layer (`app/schemas/`)
- **Pydantic models for validation**
- **API input/output contracts**
- **Types**: Base, Create, Read, Update
- **Auto-generated docs in OpenAPI**

## 🔐 Configuration (`app/config.py`)

Uses Pydantic BaseSettings to load from environment:

```python
settings.database_url      # PostgreSQL connection
settings.smtp_host         # Email server
settings.smtp_user         # Email credentials
settings.openai_api_key    # AI features
settings.generated_docs_path  # PDF storage
```

All sensitive data comes from `.env` file (not committed to git).

## 🗄️ Database Migrations (Alembic)

```
alembic/
├── env.py              # Alembic environment config
├── script.py.mako      # Migration template
└── versions/           # Migration files
    └── xxxxx_initial_migration.py
```

**Workflow**:
1. Modify models in `app/models/`
2. `alembic revision --autogenerate -m "description"`
3. Review generated migration
4. `alembic upgrade head`

## 📦 Dependencies

### Core Framework
- **FastAPI**: Modern, fast web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation

### Database
- **SQLAlchemy 2.x**: ORM
- **psycopg2-binary**: PostgreSQL driver
- **Alembic**: Migrations

### Document Generation
- **Jinja2**: Template engine
- **WeasyPrint**: HTML to PDF

### Email & AI
- **aiosmtplib**: Async SMTP client
- **openai**: OpenAI API client

## 🎯 Design Patterns

### Dependency Injection
```python
def get_job_offer(
    job_offer_id: int,
    db: Session = Depends(get_db)  # Injected
):
    ...
```

### Repository Pattern
- CRUD layer acts as repositories
- Separates data access from business logic

### Service Layer
- Business logic isolated in services
- Testable independently of HTTP layer

### DTO Pattern
- Pydantic schemas act as DTOs
- Clear contract between layers

## 🧪 Testing Strategy (Future)

```
tests/
├── unit/
│   ├── test_match_service.py
│   ├── test_draft_service.py
│   └── test_crud.py
├── integration/
│   ├── test_pipeline.py
│   └── test_api.py
└── conftest.py
```

## 🚀 Deployment Architecture (Future)

```
┌─────────────┐     ┌─────────────┐
│   Nginx     │────▶│   Gunicorn  │
│ (Reverse    │     │  + Uvicorn  │
│  Proxy)     │     │   Workers   │
└─────────────┘     └─────────────┘
                           │
                    ┌──────┴──────┐
                    │   FastAPI   │
                    │     App     │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
         ┌────▼────┐  ┌───▼────┐  ┌───▼────┐
         │ Postgres│  │  Redis │  │   S3   │
         │   DB    │  │ (Cache)│  │ (PDFs) │
         └─────────┘  └────────┘  └────────┘
```

## 📈 Scalability Considerations

### Current (MVP)
- Single server
- Synchronous operations
- Local file storage
- Direct database access

### Future Improvements
1. **Caching**: Redis for frequently accessed data
2. **Queue**: Celery for async tasks (email, PDF generation)
3. **Storage**: S3/Azure Blob for generated documents
4. **Database**: Read replicas, connection pooling
5. **Load Balancing**: Multiple API instances
6. **Monitoring**: Logging, metrics, tracing

## 🔒 Security Checklist (TODO)

- [ ] JWT authentication implementation
- [ ] Password hashing (bcrypt)
- [ ] Rate limiting
- [ ] CORS configuration (restrict origins)
- [ ] SQL injection protection (using ORM)
- [ ] Input validation (Pydantic)
- [ ] HTTPS only in production
- [ ] API key rotation
- [ ] Secrets management (not in .env)
- [ ] OWASP Top 10 compliance

## 📊 Performance Optimization (Future)

- [ ] Database query optimization
- [ ] Async database operations
- [ ] Response caching
- [ ] Lazy loading for relationships
- [ ] Connection pooling
- [ ] Background job processing
- [ ] CDN for static assets
- [ ] Database indexes (partially implemented)

## 🎓 Code Quality Standards

- **Type Hints**: All functions typed
- **Docstrings**: All public functions documented
- **Separation of Concerns**: Clear layer boundaries
- **DRY Principle**: Reusable CRUD and services
- **RESTful Design**: Proper HTTP methods and status codes
- **Consistent Naming**: Snake_case for Python, clear variable names

---

This architecture provides a solid foundation for a production-ready application tracking system.
