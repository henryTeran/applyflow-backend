"""
Draft service - generates application drafts (cover letter text + PDF).
"""

import logging
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False
    logger.warning("Jinja2 not available - PDF generation will be disabled")

try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    logger.warning("WeasyPrint not available - PDF generation will be disabled")

from app.models.job_offer import JobOffer
from app.models.application_draft import ApplicationDraft
from app.services.match_service import CandidateProfile
from app.config import settings
from app.crud import application_draft as draft_crud
from app.schemas.application_draft import ApplicationDraftCreate


class DraftService:
    """Service for generating application drafts."""
    
    def __init__(self):
        """Initialize the draft service with Jinja2 environment."""
        self.pdf_enabled = JINJA2_AVAILABLE and WEASYPRINT_AVAILABLE
        
        if self.pdf_enabled:
            template_dir = Path(__file__).parent.parent / "templates"
            if template_dir.exists():
                self.jinja_env = Environment(
                    loader=FileSystemLoader(str(template_dir)),
                    autoescape=select_autoescape(['html', 'xml'])
                )
            else:
                logger.warning(f"Template directory not found: {template_dir}")
                self.pdf_enabled = False
        else:
            logger.info("PDF generation disabled - missing dependencies")
            self.jinja_env = None
        
        # Ensure generated_docs directory exists
        self.docs_path = Path(settings.generated_docs_path)
        self.docs_path.mkdir(exist_ok=True, parents=True)
    
    def generate_cover_letter_text(
        self,
        job_offer: JobOffer,
        candidate: CandidateProfile,
        use_ai: bool = True
    ) -> str:
        """
        Generate cover letter text based on job offer and candidate profile.
        
        Args:
            job_offer: The job offer to apply for
            candidate: The candidate profile
            use_ai: Whether to use AI for generation
        
        Returns:
            Cover letter text
        """
        from app.config import settings
        
        # Try AI generation if enabled and API key available
        if use_ai and settings.openai_api_key:
            try:
                return self._generate_cover_letter_with_ai(job_offer, candidate, settings.openai_api_key)
            except Exception as e:
                logger.warning(f"AI generation failed, falling back to template: {e}")
        
        # Fallback to template-based generation
        candidate_title = candidate.title.strip() if candidate.title else ""
        title_phrase = candidate_title if candidate_title else "professional"

        education_phrase = ""
        if candidate.education_level and candidate.field_of_study:
            education_phrase = f" I hold a {candidate.education_level} degree in {candidate.field_of_study}."
        elif candidate.education_level:
            education_phrase = f" I hold a {candidate.education_level} degree."

        location_phrase = candidate.preferred_locations[0] if candidate.preferred_locations else ""
        availability_phrase = ", ".join(candidate.preferred_job_types) if candidate.preferred_job_types else ""

        cover_letter = f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job_offer.title} position at {job_offer.company}. With {candidate.years_of_experience} years of experience in software engineering and a proven track record in delivering high-quality solutions, I am confident that I would be a valuable addition to your team.

My technical expertise includes {', '.join(candidate.technical_skills[:5])}, and more. I have successfully worked on projects in {', '.join(candidate.industry_experience) if candidate.industry_experience else 'various industries'}, which aligns well with your company's domain.

I am particularly excited about this opportunity because:
- The role aligns with my career goals as a {title_phrase}
- {job_offer.company} is known for innovation and excellence
- The position offers opportunities to work with cutting-edge technologies

{f'I am based in {location_phrase}.' if location_phrase else ''}{f' I am available for {availability_phrase} opportunities.' if availability_phrase else ''}{education_phrase}

I would welcome the opportunity to discuss how my skills and experience can contribute to {job_offer.company}'s success. Thank you for considering my application.

Best regards,
{candidate.name}
"""
        return cover_letter
    
    def _generate_cover_letter_with_ai(
        self,
        job_offer: JobOffer,
        candidate: CandidateProfile,
        openai_api_key: str
    ) -> str:
        """
        Generate personalized cover letter using OpenAI.
        
        Args:
            job_offer: The job offer
            candidate: The candidate profile
            openai_api_key: OpenAI API key
        
        Returns:
            Generated cover letter text
        """
        from openai import OpenAI
        
        client = OpenAI(api_key=openai_api_key)
        
        prompt = f"""Write a professional and personalized cover letter for the following job application:

**Candidate Profile:**
- Name: {candidate.name}
- Title: {candidate.title}
- Experience: {candidate.years_of_experience} years
- Technical Skills: {', '.join(candidate.technical_skills[:10])}
- Education: {candidate.education_level} in {candidate.field_of_study}
- Languages: {', '.join(candidate.languages)}

**Job Offer:**
- Position: {job_offer.title}
- Company: {job_offer.company}
- Location: {job_offer.location or 'Not specified'}
- Description: {job_offer.raw_description[:1500]}

Requirements:
1. Professional tone, enthusiastic but not over the top
2. Highlight relevant skills and experience matching the job description
3. Show genuine interest in the company and role
4. Keep it concise (3-4 paragraphs, max 300 words)
5. End with a call to action
6. Do NOT include address blocks or dates (just the letter body)

Write the cover letter now:"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert career coach and cover letter writer. Write compelling, personalized cover letters that highlight the candidate's strengths."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        cover_letter = response.choices[0].message.content.strip()
        logger.info(f"Generated cover letter with AI ({len(cover_letter)} characters)")
        
        return cover_letter
    
    def generate_cover_letter_pdf(
        self,
        job_offer: JobOffer,
        cover_letter_text: str,
        candidate: CandidateProfile
    ) -> str | None:
        """
        Generate a PDF cover letter using WeasyPrint and Jinja2 template.
        
        Args:
            job_offer: The job offer
            cover_letter_text: The cover letter text
            candidate: The candidate profile
        
        Returns:
            Path to the generated PDF file, or None if PDF generation is disabled
        """
        if not self.pdf_enabled:
            logger.warning("PDF generation disabled - skipping PDF creation")
            return None
        
        try:
            # Render HTML template
            template = self.jinja_env.get_template("cover_letter_base.html")
            
            html_content = template.render(
                candidate_name=candidate.name,
                candidate_title=candidate.title,
                candidate_email="john.doe@example.com",  # TODO: Get from settings
                candidate_phone="+41 XX XXX XX XX",  # TODO: Get from settings
                company=job_offer.company,
                position=job_offer.title,
                cover_letter_text=cover_letter_text,
                date=datetime.now().strftime("%B %d, %Y")
            )
            
            # Generate PDF filename
            safe_company = "".join(c for c in job_offer.company if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_company = safe_company.replace(' ', '_')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_filename = f"cover_letter_{safe_company}_{timestamp}.pdf"
            pdf_path = self.docs_path / pdf_filename
            
            # Generate PDF with WeasyPrint
            HTML(string=html_content).write_pdf(str(pdf_path))
            
            return str(pdf_path)
        except Exception as e:
            logger.error(f"Failed to generate PDF: {e}", exc_info=True)
            return None
    
    def generate_email_content(
        self,
        job_offer: JobOffer,
        candidate: CandidateProfile
    ) -> tuple[str, str]:
        """
        Generate email subject and body for the application.
        
        Args:
            job_offer: The job offer
            candidate: The candidate profile
        
        Returns:
            Tuple of (subject, body)
        """
        subject = f"Application for {job_offer.title} position"
        
        body = f"""Dear Hiring Manager,

Please find attached my application for the {job_offer.title} position at {job_offer.company}.

I have included:
- My cover letter
- My CV/Resume

I am very interested in this opportunity and look forward to hearing from you.

Best regards,
{candidate.name}
"""
        
        return subject, body
    
    def create_application_draft(
        self,
        db: Session,
        job_offer: JobOffer,
        candidate: CandidateProfile,
        user_id: int = None
    ) -> ApplicationDraft:
        """
        Create a complete application draft for a job offer.
        
        This generates:
        - Cover letter text
        - Cover letter PDF
        - Email subject and body
        
        Args:
            db: Database session
            job_offer: The job offer to create a draft for
            candidate: The candidate profile
            user_id: The user ID for the draft
        
        Returns:
            ApplicationDraft object
        """
        # Generate cover letter
        cover_letter_text = self.generate_cover_letter_text(job_offer, candidate)
        
        # Try to generate PDF (may return None if PDF generation is disabled)
        cover_letter_pdf_path = None
        try:
            cover_letter_pdf_path = self.generate_cover_letter_pdf(
                job_offer, cover_letter_text, candidate
            )
            if cover_letter_pdf_path:
                logger.info(f"PDF generated: {cover_letter_pdf_path}")
            else:
                logger.info("PDF generation skipped (dependencies not available)")
        except Exception as e:
            logger.warning(f"Failed to generate PDF, continuing without it: {e}")
        
        # Generate email content
        email_subject, email_body = self.generate_email_content(job_offer, candidate)
        
        # Create draft in database
        draft_data = ApplicationDraftCreate(
            job_offer_id=job_offer.id,
            cover_letter_text=cover_letter_text,
            cover_letter_pdf_path=cover_letter_pdf_path,
            email_subject=email_subject,
            email_body=email_body,
            status="ready"
        )
        
        draft = draft_crud.create(db, draft_data, user_id)
        return draft


# Global instance
draft_service = DraftService()


def generate_application_draft(job_offer_id: int, user_id: int, db) -> 'ApplicationDraft':
    """
    Generate a complete application draft for a job offer.
    
    Args:
        job_offer_id: The job offer ID
        user_id: The user ID
        db: Database session
    
    Returns:
        ApplicationDraft object
    """
    from app.crud import job_offer as job_offer_crud
    from app.crud import user as user_crud
    from app.services.match_service import extract_profile_from_user
    
    # Get job offer with user_id filter
    job_offer = job_offer_crud.get(db, job_offer_id, user_id)
    if not job_offer:
        raise ValueError(f"Job offer {job_offer_id} not found")
    
    # Get user and extract candidate profile
    user = user_crud.get(db, user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")
    
    candidate_profile = extract_profile_from_user(user)
    
    # Generate draft with candidate profile
    draft = draft_service.create_application_draft(db, job_offer, candidate_profile, user_id)
    return draft
