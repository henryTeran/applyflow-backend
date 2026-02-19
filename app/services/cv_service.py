"""
CV parsing service - extracts text and structured data from CV files.
"""

import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)

# Try to import PDF parsing libraries
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    logger.warning("PyPDF2 not available - CV text extraction will be limited")


# ============================================================================
# UTILITY FUNCTIONS FOR TEXT CLEANING AND NORMALIZATION
# ============================================================================

def _clean_cv_text(raw_text: str) -> str:
    """
    Clean and normalize CV text extracted from PDF.
    
    This function:
    - Removes excessive whitespace and newlines
    - Normalizes section headers (EXPERIENCE, PROJECTS, EDUCATION, etc.)
    - Removes page break markers
    - Collapses multiple blank lines into single ones
    
    Args:
        raw_text: Raw text extracted from PDF
    
    Returns:
        Cleaned text
    """
    if not raw_text:
        return ""
    
    text = raw_text
    
    # Remove page break markers (we don't need them after extraction)
    text = re.sub(r'---\s*PAGE\s+BREAK\s*---', '', text, flags=re.IGNORECASE)
    
    # Normalize common section headers (make them consistent)
    # This helps the AI identify sections more reliably
    section_patterns = [
        (r'\s*COMPETENC(IES|Y)\s*', '\n\n=== COMPETENCIES ===\n'),
        (r'\s*EXPERIENCE\s*', '\n\n=== EXPERIENCE ===\n'),
        (r'\s*PROJECTS?\s*', '\n\n=== PROJECTS ===\n'),
        (r'\s*EDUCATION\s*', '\n\n=== EDUCATION ===\n'),
        (r'\s*AWARDS?\s*', '\n\n=== AWARDS ===\n'),
        (r'\s*CERTIFICATIONS?\s*', '\n\n=== CERTIFICATIONS ===\n'),
        (r'\s*SKILLS?\s*', '\n\n=== SKILLS ===\n'),
    ]
    
    for pattern, replacement in section_patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # Collapse multiple spaces into single space (except at line start for indentation)
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Collapse multiple newlines into maximum 2 newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    # Final cleanup: remove leading/trailing whitespace from entire text
    text = text.strip()
    
    logger.debug(f"Cleaned CV text: {len(raw_text)} -> {len(text)} chars")
    return text


def _identify_orphan_dates(text: str) -> str:
    """
    Identify and mark blocks of orphan dates (dates appearing alone without context).
    
    Orphan dates are common in PDF extraction when layout columns are parsed sequentially.
    For example, a CV with dates in the right margin will have all dates extracted together
    at the end, separated from their corresponding experiences/projects.
    
    This function identifies such blocks and marks them so the AI can reassociate them.
    
    Args:
        text: Cleaned CV text
    
    Returns:
        Text with orphan date blocks marked
    """
    # Pattern to detect lines that are ONLY dates (e.g., "05/2021 - 11/2023", "2025/05 – 06/2025")
    # This regex matches common date range formats
    date_line_pattern = r'^\s*\d{1,2}[/\-\.]\d{2,4}\s*[-–—]\s*\d{1,2}[/\-\.]\d{2,4}\s*$'
    
    lines = text.split('\n')
    result_lines = []
    orphan_date_block = []
    in_orphan_block = False
    
    for i, line in enumerate(lines):
        # Check if this line is a date-only line
        if re.match(date_line_pattern, line.strip()):
            orphan_date_block.append(line)
            in_orphan_block = True
        else:
            # If we were collecting orphan dates, mark them
            if in_orphan_block and orphan_date_block:
                result_lines.append('\n[ORPHAN_DATES_BLOCK - likely belong to previous PROJECTS or EXPERIENCE section]:')
                result_lines.extend(orphan_date_block)
                result_lines.append('[END_ORPHAN_DATES_BLOCK]\n')
                orphan_date_block = []
                in_orphan_block = False
            
            result_lines.append(line)
    
    # Handle case where document ends with orphan dates
    if orphan_date_block:
        result_lines.append('\n[ORPHAN_DATES_BLOCK - likely belong to previous PROJECTS or EXPERIENCE section]:')
        result_lines.extend(orphan_date_block)
        result_lines.append('[END_ORPHAN_DATES_BLOCK]\n')
    
    return '\n'.join(result_lines)


def _preprocess_cv_text(raw_text: str) -> str:
    """
    Complete preprocessing pipeline for CV text.
    
    Applies all cleaning and normalization steps:
    1. Basic cleaning (whitespace, section headers)
    2. Orphan date identification
    
    Args:
        raw_text: Raw text from PDF extraction
    
    Returns:
        Preprocessed text ready for AI processing
    """
    text = _clean_cv_text(raw_text)
    text = _identify_orphan_dates(text)
    logger.info(f"Preprocessed CV text: {len(text)} chars")
    return text


# ============================================================================
# MAIN CV PROCESSING FUNCTIONS
# ============================================================================

def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
    
    Returns:
        Extracted text or None if extraction fails
    """
    if not PYPDF2_AVAILABLE:
        logger.warning("PyPDF2 not available - cannot extract text from PDF")
        return None
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text_parts = []
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            
            # Join all pages with clear page breaks
            full_text = "\n--- PAGE BREAK ---\n".join(text_parts)
            
            if not full_text.strip():
                logger.warning(f"No text extracted from {pdf_path}")
                return None
            
            logger.info(f"Successfully extracted {len(full_text)} characters from {pdf_path} ({len(text_parts)} pages)")
            return full_text
            
    except Exception as e:
        logger.error(f"Failed to extract text from {pdf_path}: {e}", exc_info=True)
        return None


def restructure_cv_text_with_ai(cv_text: str, openai_api_key: Optional[str] = None) -> Optional[str]:
    """
    Use AI to restructure and clean the extracted CV text, preserving chronological order.
    
    This function uses GPT-4o to intelligently reorganize disordered CV text that was
    extracted from PDF. It handles common issues like:
    - Dates separated from their experiences/projects
    - Sections in wrong order
    - Information scattered across pages
    
    Args:
        cv_text: The raw extracted CV text
        openai_api_key: OpenAI API key
    
    Returns:
        Restructured CV text in proper order, or original text if AI unavailable
    """
    if not openai_api_key:
        logger.warning("OpenAI API key not configured - cannot restructure CV text")
        return cv_text  # Return original text
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=openai_api_key)
        
        # Preprocess the text before sending to AI
        preprocessed_text = _preprocess_cv_text(cv_text)
        
        # Improved prompt with stronger structure and explicit instructions
        prompt = f"""You are a CV restructuring expert. The following text was extracted from a PDF CV but is in disorder.

CRITICAL INSTRUCTIONS:
1. **Reorganize the CV in this EXACT order**:
   - Section 1: Personal Information (name, contact details, location, title/role)
   - Section 2: Professional Summary (if present)
   - Section 3: Skills (separate Technical Skills and Soft Skills)
   - Section 4: Work Experience (chronological order, MOST RECENT FIRST)
   - Section 5: Projects (chronological order, MOST RECENT FIRST)
   - Section 6: Education (chronological order, MOST RECENT FIRST)
   - Section 7: Certifications and Awards

2. **Reassociate orphan dates**: The text may contain date blocks marked as [ORPHAN_DATES_BLOCK]. These dates belong to the projects or experiences that appear BEFORE them. Match each date to its corresponding entry based on:
   - Chronological order (most recent dates go with most recent projects)
   - Number of entries vs number of dates
   - Context clues in the descriptions

3. **For each entry (experience/project/education)**:
   - Place the date IMMEDIATELY after the title/company name on the same line or next line
   - Format: "Title/Company - Date Range" or "Title - Date Range"
   - Keep all details, descriptions, and bullet points

4. **Preserve ALL information**: Do not remove, summarize, or omit any content. Every detail from the original must appear in the output.

5. **Output format**: Return ONLY the restructured CV text. Do not add comments like "Here is the restructured CV" or explanations. Start directly with the person's name.

Raw CV Text:
{preprocessed_text}"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a professional CV restructuring assistant. Your task is to reorganize disordered CV text into a clear, chronological format while preserving every piece of information. You must reassociate separated dates with their corresponding experiences and projects."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Lower temperature for more consistent formatting
            max_tokens=5000   # Increased to handle longer CVs
        )
        
        restructured_text = response.choices[0].message.content.strip()
        
        # Remove any potential AI-added preamble
        if restructured_text.lower().startswith(('here is', 'here\'s', 'below is')):
            lines = restructured_text.split('\n')
            restructured_text = '\n'.join(lines[1:]).strip()
        
        logger.info(f"Successfully restructured CV text ({len(restructured_text)} chars from {len(cv_text)} original)")
        return restructured_text
        
    except Exception as e:
        logger.error(f"Failed to restructure CV text with AI: {e}", exc_info=True)
        return cv_text  # Return original on error


def parse_cv_with_ai(cv_text: str, openai_api_key: Optional[str] = None) -> dict:
    """
    Parse CV text using AI to extract structured information.
    
    This function sends the CV text to GPT-4o-mini to extract structured data
    such as name, skills, experience, education, etc.
    
    Args:
        cv_text: The CV text content (preferably already cleaned/restructured)
        openai_api_key: OpenAI API key
    
    Returns:
        Dictionary with structured CV data. Always includes 'parsed' boolean field.
    """
    if not openai_api_key:
        logger.warning("OpenAI API key not configured - using basic parsing")
        return {
            "parsed": False,
            "raw_text": cv_text,
            "skills": [],
            "experience_years": None,
            "education": None
        }
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=openai_api_key)
        
        # Clean the text before sending (in case it wasn't already cleaned)
        clean_text = _clean_cv_text(cv_text)
        
        # Limit to 8000 characters to avoid token limits
        text_to_send = clean_text[:8000]
        
        prompt = f"""Analyze this CV and extract the following information in JSON format:
- name: Full name
- title: Current professional title
- contact_email: Email address
- contact_phone: Phone number
- location: City/Country
- years_of_experience: Estimated years of experience (integer)
- technical_skills: List of technical skills
- soft_skills: List of soft skills
- languages: List of languages with proficiency
- education_level: Highest education level
- field_of_study: Field of study
- certifications: List of certifications
- key_experiences: List of 3-5 most relevant job positions with company and role
- summary: Brief professional summary (2-3 sentences)

CV Text:
{text_to_send}

Return ONLY valid JSON, no other text."""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a CV parsing assistant. Extract structured information from CVs and return it as valid JSON. Return ONLY the JSON object, no markdown formatting, no explanations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Attempt to parse JSON - with fallback for common issues
        import json
        try:
            # Try direct parse first
            parsed_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.warning(f"Initial JSON parse failed: {e}. Attempting to extract JSON from response.")
            
            # Fallback: try to extract JSON from markdown code blocks or text with preamble
            # Remove markdown code fences if present
            cleaned_response = re.sub(r'```json\s*', '', response_text)
            cleaned_response = re.sub(r'```\s*$', '', cleaned_response)
            
            # Try to find the first { and last }
            first_brace = cleaned_response.find('{')
            last_brace = cleaned_response.rfind('}')
            
            if first_brace != -1 and last_brace != -1:
                json_candidate = cleaned_response[first_brace:last_brace + 1]
                try:
                    parsed_data = json.loads(json_candidate)
                    logger.info("Successfully extracted JSON after cleanup")
                except json.JSONDecodeError as e2:
                    logger.error(f"Failed to parse JSON even after cleanup: {e2}")
                    logger.error(f"Response was: {response_text[:500]}")
                    return {
                        "parsed": False,
                        "raw_text": cv_text,
                        "error": f"JSON parsing failed: {str(e2)}"
                    }
            else:
                logger.error("Could not find JSON object in response")
                logger.error(f"Response was: {response_text[:500]}")
                return {
                    "parsed": False,
                    "raw_text": cv_text,
                    "error": "No JSON object found in AI response"
                }
        
        # Add parsed flag
        parsed_data["parsed"] = True
        
        logger.info(f"Successfully parsed CV with AI - extracted {len(parsed_data)} fields")
        return parsed_data
        
    except Exception as e:
        logger.error(f"Failed to parse CV with AI: {e}", exc_info=True)
        return {
            "parsed": False,
            "raw_text": cv_text,
            "error": str(e)
        }
