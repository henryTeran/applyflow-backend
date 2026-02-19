"""
AI service - wrapper for OpenAI API calls.

This module provides AI-powered features using OpenAI GPT models.
"""

from typing import Optional
from openai import OpenAI
from app.config import settings
from app.models.job_offer import JobOffer
from app.services.match_service import CandidateProfile
from app.logging_config import get_logger

logger = get_logger(__name__)


class AIService:
    """Service for AI-powered features using OpenAI API."""
    
    def __init__(self):
        """Initialize AI service with OpenAI client."""
        self.api_key = settings.openai_api_key
        self.client = None
        
        if self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                logger.warning("openai_init_failed", error=str(e))
    
    def _call_gpt(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.7
    ) -> Optional[str]:
        """
        Make a call to OpenAI GPT API.
        
        Args:
            system_prompt: System instructions for the model
            user_prompt: User message/query
            model: Model to use
            temperature: Creativity level (0-1)
            
        Returns:
            Model response text or None if failed
        """
        if not self.client:
            return None
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error("gpt_api_call_failed", error=str(e), model=model)
            return None
    
    def generate_match_analysis(
        self,
        job_offer: JobOffer,
        candidate_profile: CandidateProfile
    ) -> dict:
        """
        Generate AI-powered match analysis between job offer and candidate.
        
        Args:
            job_offer: The job offer to analyze
            candidate_profile: The candidate profile to match against
        
        Returns:
            Dictionary with analysis results including score, reasons, skills, etc.
        """
        if not self.client:
            return {
                'score': 0.0,
                'reasons': 'AI service not configured',
                'skills_detected': [],
                'red_flags': [],
                'suggestions': 'Configure OpenAI API key to enable AI-powered matching'
            }
        
        system_prompt = """You are an expert career advisor and recruiter analyzing job-candidate matches.
Provide detailed, honest analysis with specific reasons and actionable suggestions.
Return your response as a structured JSON with these exact keys:
- score: float between 0 and 100
- reasons: string with detailed explanation
- skills_detected: array of required skills found in job description
- red_flags: array of potential concerns or mismatches
- suggestions: string with advice for tailoring the application"""

        user_prompt = f"""Analyze this job offer for the candidate:

CANDIDATE PROFILE:
- Name: {candidate_profile.name}
    - Title: {candidate_profile.title or 'Not provided'}
    - Technical Skills: {', '.join(candidate_profile.technical_skills[:20]) if candidate_profile.technical_skills else 'Not provided'}
    - Soft Skills: {', '.join(candidate_profile.soft_skills[:20]) if candidate_profile.soft_skills else 'Not provided'}
    - Years of Experience (estimated): {candidate_profile.years_of_experience}
    - Education: {candidate_profile.education_level or 'Not provided'} {('in ' + candidate_profile.field_of_study) if candidate_profile.field_of_study else ''}
    - Languages: {', '.join(candidate_profile.languages) if candidate_profile.languages else 'Not provided'}

JOB OFFER:
- Title: {job_offer.title}
- Company: {job_offer.company}
- Location: {job_offer.location}
- Description:
{job_offer.raw_description}

Provide a comprehensive match analysis."""

        try:
            import json
            response = self._call_gpt(system_prompt, user_prompt, temperature=0.3)
            if response:
                # Try to parse JSON from response
                result = json.loads(response)
                return result
        except Exception as e:
            logger.error("match_analysis_failed", error=str(e), job_id=job_offer.id)
        
        return {
            'score': 0.0,
            'reasons': 'Failed to generate AI analysis',
            'skills_detected': [],
            'red_flags': [],
            'suggestions': 'Please try again or check your OpenAI API configuration'
        }
    
    def generate_cover_letter(
        self,
        job_offer: JobOffer,
        candidate_profile: CandidateProfile,
        tone: str = "professional"
    ) -> str:
        """
        Generate AI-powered cover letter tailored to the job offer.
        
        Args:
            job_offer: The job offer to write a cover letter for
            candidate_profile: The candidate profile
            tone: Writing tone ("professional", "enthusiastic", "formal", etc.)
        
        Returns:
            Generated cover letter text
        """
        if not self.client:
            return "AI service not configured. Please add OPENAI_API_KEY to .env file."
        
        system_prompt = f"""You are an expert career writer specializing in compelling cover letters.
Write cover letters that are:
- Authentic and personalized
- {tone} in tone
- 250-350 words in length
- Focused on value proposition and fit
- Free of clichés and generic statements
- Formatted with proper paragraphs

Do not include address headers or dates - just the letter body."""

        user_prompt = f"""Write a compelling cover letter for this application:

CANDIDATE:
- Name: {candidate_profile.name}
    - Title: {candidate_profile.title or 'Not provided'}
    - Skills: {', '.join(candidate_profile.technical_skills[:10]) if candidate_profile.technical_skills else 'Not provided'}
    - Experience: {candidate_profile.years_of_experience} years
    - Education: {candidate_profile.education_level or 'Not provided'}
- Key Strengths: {', '.join(candidate_profile.soft_skills[:5])}

JOB OFFER:
- Position: {job_offer.title}
- Company: {job_offer.company}
- Location: {job_offer.location}
- Description:
{job_offer.raw_description[:1500]}

Write a cover letter that highlights why {candidate_profile.name} is an excellent fit for this role.
Focus on specific skills and experiences that match the job requirements."""

        response = self._call_gpt(system_prompt, user_prompt, temperature=0.8)
        
        if response:
            return response.strip()
        
        return "Failed to generate cover letter. Please check your OpenAI API configuration."
    
    def optimize_application_text(
        self,
        original_text: str,
        job_offer: JobOffer,
        optimization_goal: str = "improve clarity and impact"
    ) -> str:
        """
        Optimize application text (cover letter, email, etc.) using AI.
        
        Args:
            original_text: The text to optimize
            job_offer: The job offer context
            optimization_goal: What to optimize for
        
        Returns:
            Optimized text
        """
        if not self.client:
            return original_text
        
        system_prompt = """You are an expert editor specializing in job application materials.
Improve the text while maintaining the author's voice and key points.
Focus on clarity, impact, and professional tone."""

        user_prompt = f"""Optimize this application text for a job at {job_offer.company}:

ORIGINAL TEXT:
{original_text}

JOB CONTEXT:
- Position: {job_offer.title}
- Company: {job_offer.company}

GOAL: {optimization_goal}

Provide the improved version, keeping the same approximate length."""

        response = self._call_gpt(system_prompt, user_prompt, temperature=0.5)
        
        return response.strip() if response else original_text
    
    def extract_job_details(self, raw_description: str) -> dict:
        """
        Extract structured information from a raw job description.
        
        Args:
            raw_description: Raw job posting text
        
        Returns:
            Dictionary with extracted details
        """
        if not self.client:
            return {
                'required_skills': [],
                'preferred_skills': [],
                'years_experience': 0,
                'education_requirements': '',
                'key_responsibilities': [],
                'benefits': []
            }
        
        system_prompt = """You are an expert at extracting structured information from job postings.
Extract key details and return them as JSON with these exact keys:
- required_skills: array of must-have skills
- preferred_skills: array of nice-to-have skills
- years_experience: number (0 if not specified)
- education_requirements: string description
- key_responsibilities: array of main duties
- benefits: array of benefits/perks mentioned"""

        user_prompt = f"""Extract structured information from this job description:

{raw_description}

Return only valid JSON."""

        try:
            import json
            response = self._call_gpt(system_prompt, user_prompt, temperature=0.2)
            if response:
                result = json.loads(response)
                return result
        except Exception as e:
            logger.error("job_details_extraction_failed", error=str(e), job_id=job_offer.id)
        
        return {
            'required_skills': [],
            'preferred_skills': [],
            'years_experience': 0,
            'education_requirements': '',
            'key_responsibilities': [],
            'benefits': []
        }


# Global instance
ai_service = AIService()
