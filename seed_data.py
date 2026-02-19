"""
Test data seeder - creates sample data for testing.

Run this after setting up the database to populate it with test data.
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.crud import job_offer as job_offer_crud
from app.crud import user as user_crud
from app.schemas.job_offer import JobOfferCreate
from app.schemas.user import UserCreate


def create_sample_user(db: Session):
    """Create a sample user."""
    user_data = UserCreate(
        email="john.doe@example.com",
        name="John Doe",
        password="changeme123"  # TODO: This will be hashed in production
    )
    
    # Check if user already exists
    existing = user_crud.get_by_email(db, user_data.email)
    if existing:
        print(f"✅ User already exists: {user_data.email}")
        return existing
    
    user = user_crud.create(db, user_data)
    print(f"✅ Created user: {user.email}")
    return user


def create_sample_job_offers(db: Session):
    """Create sample job offers."""
    sample_jobs = [
        JobOfferCreate(
            title="Senior Python Developer",
            company="TechCorp SA",
            location="Geneva, Switzerland",
            source="LinkedIn",
            url="https://linkedin.com/jobs/123",
            application_type="email",
            application_url="careers@techcorp.ch",
            raw_description="""
We are looking for a Senior Python Developer to join our team in Geneva.

Requirements:
- 5+ years of Python development experience
- Strong experience with FastAPI, Django, or Flask
- Experience with PostgreSQL and SQLAlchemy
- Knowledge of REST APIs and microservices
- Docker and Kubernetes experience
- Excellent communication skills in English and French

Nice to have:
- Experience with AWS or Azure
- Knowledge of React or Vue.js
- Agile/Scrum experience

We offer:
- Competitive salary
- Flexible working hours
- Remote work options
- Health insurance
- Professional development opportunities
            """
        ),
        JobOfferCreate(
            title="Full Stack Engineer",
            company="StartupHub",
            location="Lausanne, Switzerland",
            source="Jobup",
            url="https://jobup.ch/jobs/456",
            application_type="portal",
            application_url="https://startuphub.ch/careers/apply",
            raw_description="""
Join our fast-growing startup as a Full Stack Engineer!

What we're looking for:
- 3+ years of web development experience
- Strong JavaScript/TypeScript skills
- Experience with React and Node.js
- Database design (PostgreSQL, MongoDB)
- RESTful API design
- Git and CI/CD workflows

Bonus points:
- Python/FastAPI experience
- GraphQL knowledge
- Experience with Vercel or Netlify
- Open source contributions

What we offer:
- Equity package
- Modern tech stack
- Flat hierarchy
- Work-life balance
            """
        ),
        JobOfferCreate(
            title="Backend Developer - Python",
            company="CERN",
            location="Meyrin, Switzerland",
            source="CERN Careers",
            url="https://careers.cern/jobs/789",
            application_type="portal",
            portal_type="cern",
            application_url="https://careers.cern/apply/789",
            raw_description="""
CERN is seeking a Backend Developer to work on scientific computing projects.

Requirements:
- Master's degree in Computer Science or related field
- 4+ years of Python development
- Experience with distributed systems
- Knowledge of REST APIs and microservices
- Strong algorithmic and problem-solving skills
- Experience with Linux and shell scripting

Desirable:
- PhD in Computer Science or Physics
- Experience with scientific computing
- Knowledge of C++ or Java
- Experience with large-scale data processing
- Knowledge of particle physics

Contract: 2 years (renewable)
Language: English required, French advantageous
            """
        ),
        JobOfferCreate(
            title="DevOps Engineer",
            company="FinanceGO",
            location="Zurich, Switzerland",
            source="LinkedIn",
            url="https://linkedin.com/jobs/999",
            application_type="email",
            application_url="hr@financego.ch",
            raw_description="""
Looking for a DevOps Engineer to join our FinTech platform team.

Must have:
- 3+ years DevOps/SRE experience
- Strong Docker and Kubernetes knowledge
- CI/CD pipeline experience (Jenkins, GitLab CI, GitHub Actions)
- Infrastructure as Code (Terraform, Ansible)
- Cloud platforms (AWS, Azure, or GCP)
- Monitoring and logging (Prometheus, Grafana, ELK)

Nice to have:
- Python or Go scripting
- Security best practices
- Financial services experience
- Certifications (AWS, CKA)

Benefits:
- CHF 100-130k depending on experience
- Full remote possible
- Learning budget
- Modern tools and technologies
            """
        ),
        JobOfferCreate(
            title="Junior Python Developer",
            company="WebSolutions",
            location="Bern, Switzerland",
            source="Indeed",
            url="https://indeed.ch/jobs/111",
            application_type="linkedin_easy_apply",
            raw_description="""
Entry-level Python Developer position for recent graduates or career changers.

Requirements:
- Bachelor's degree or bootcamp certificate
- 1-2 years Python experience (projects, internships, or personal)
- Basic understanding of web development
- Knowledge of Git
- Enthusiasm to learn!

We teach you:
- Professional development practices
- Modern frameworks (FastAPI, Django)
- Database design
- Testing and deployment
- Team collaboration

Great opportunity for career starters!
Salary: CHF 70-85k
            """
        )
    ]
    
    created_jobs = []
    for job_data in sample_jobs:
        # Check if similar job exists
        existing_jobs = job_offer_crud.list_job_offers(
            db,
            company=job_data.company,
            limit=1
        )
        
        if existing_jobs and existing_jobs[0].title == job_data.title:
            print(f"⏭️  Skipping (already exists): {job_data.title} at {job_data.company}")
            created_jobs.append(existing_jobs[0])
            continue
        
        job = job_offer_crud.create(db, job_data)
        created_jobs.append(job)
        print(f"✅ Created job offer: {job.title} at {job.company}")
    
    return created_jobs


def main():
    """Main seeding function."""
    print("🌱 Seeding database with sample data...")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        # Create sample user
        print("\n📝 Creating sample user...")
        user = create_sample_user(db)
        
        # Create sample job offers
        print("\n💼 Creating sample job offers...")
        jobs = create_sample_job_offers(db)
        
        print("\n" + "="*60)
        print(f"✅ Seeding complete!")
        print(f"   - Created/verified 1 user")
        print(f"   - Created/verified {len(jobs)} job offers")
        print("="*60)
        print("\n💡 Next steps:")
        print("1. Run the pipeline on a job: POST /api/v1/job-offers/1/run-pipeline")
        print("2. Check the matches: GET /api/v1/job-matches/")
        print("3. View drafts: GET /api/v1/drafts/")
        print("\n🚀 Happy testing!")
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
