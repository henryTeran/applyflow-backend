"""app.services.match_service

Matching entre une offre (JobOffer) et un profil candidat (CandidateProfile).

Objectif (2026-01): utiliser les données extraites du CV de l'utilisateur et
éviter d'utiliser un profil "par défaut" pour le scoring en production.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import logging
import re
from typing import Iterable, List, Optional

from app.models.job_offer import JobOffer

logger = logging.getLogger(__name__)


@dataclass
class CandidateProfile:
    """Candidate profile for matching against job offers."""
    
    # Core information
    name: str
    title: str
    years_of_experience: int
    
    # Skills
    technical_skills: List[str]
    soft_skills: List[str]
    languages: List[str]
    
    # Education
    education_level: str  # "Bachelor", "Master", "PhD", etc.
    field_of_study: str
    
    # Preferences
    preferred_locations: List[str]
    preferred_job_types: List[str]  # "full-time", "contract", "remote", etc.
    
    # Additional
    certifications: List[str]
    industry_experience: List[str]


@dataclass
class MatchResult:
    """Result of a match analysis."""
    score: float  # 0-100
    reasons: str
    skills_detected: str
    red_flags: str


def _normalize_for_match(text: str) -> str:
    text = (text or "").lower()
    # Normalise certains séparateurs fréquents
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    text = text.replace("â€“", "-")
    # Remplace tout ce qui n'est pas lettre/chiffre/+/#/./- par des espaces
    text = re.sub(r"[^a-z0-9+#.\-]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _normalize_for_match_loose(text: str) -> str:
    """Normalisation plus permissive: traite '.', '-' et '/' comme séparateurs.

    Utile pour matcher des variantes comme:
    - Node.js vs Node JS
    - CI/CD vs CICD
    - end-to-end vs end to end
    """
    t = _normalize_for_match(text)
    if not t:
        return ""
    t = t.replace(".", " ").replace("-", " ").replace("/", " ")
    return re.sub(r"\s+", " ", t).strip()


def _iter_skill_candidates(text: str) -> Iterable[str]:
    if not text:
        return []
    # Split large: lignes, virgules, points-virgules, pipes, bullets, slash.
    parts = re.split(r"[\n,;|•·\u2022/]+", text)
    for part in parts:
        cleaned = part.strip(" \t-–—:·•")
        cleaned = re.sub(r"\s+", " ", cleaned)
        if not cleaned:
            continue
        # Évite les catégories trop génériques
        if len(cleaned) < 2:
            continue
        yield cleaned


def _dedupe_preserve_order(items: Iterable[str]) -> List[str]:
    seen: set[str] = set()
    out: List[str] = []
    for item in items:
        key = _normalize_for_match(item)
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(item.strip())
    return out


def _contains_skill(job_text_norm: str, skill: str) -> bool:
    """Match plus robuste que `in`: boundary-friendly sur texte normalisé."""
    skill_norm = _normalize_for_match(skill)
    if not skill_norm:
        return False

    job_text_loose = _normalize_for_match_loose(job_text_norm)
    skill_loose = _normalize_for_match_loose(skill)

    # Cas simples: tokens sans espaces
    if " " not in skill_norm:
        # Word boundary approximée: entouré d'espaces ou début/fin
        if re.search(rf"(?:^| )({re.escape(skill_norm)})(?:$| )", job_text_norm) is not None:
            return True
        if skill_loose and re.search(rf"(?:^| )({re.escape(skill_loose)})(?:$| )", job_text_loose) is not None:
            return True
        return False

    # Skill multi-mots: recherche substring normalisée
    if skill_norm in job_text_norm:
        return True
    if skill_loose and skill_loose in job_text_loose:
        return True
    return False


def _infer_years_of_experience_from_text(*texts: Optional[str]) -> int:
    combined = "\n".join([t for t in texts if t])
    if not combined:
        return 0

    years = [int(y) for y in re.findall(r"\b(19\d{2}|20\d{2})\b", combined)]
    if not years:
        return 0

    earliest = min(years)
    current_year = date.today().year
    # Heuristique simple: maintenant - année la plus ancienne
    return max(0, current_year - earliest)


def _infer_education_level(text: Optional[str]) -> str:
    t = _normalize_for_match(text or "")
    if not t:
        return ""
    if "phd" in t or "doctorat" in t:
        return "PhD"
    if "master" in t or "msc" in t or "bac+5" in t:
        return "Master"
    if "bachelor" in t or "licence" in t or "bac+3" in t:
        return "Bachelor"
    return ""


def compute_match_score(
    job_offer: JobOffer,
    candidate: CandidateProfile
) -> MatchResult:
    """
    Compute a match score between a job offer and candidate profile.
    
    Implémentation rule-based améliorée.
    - Utilise les compétences issues du CV (candidate.*) au lieu d'un profil fictif.
    - Scoring conçu pour être stable et explicable.
    
    Args:
        job_offer: The job offer to match against
        candidate: The candidate profile
    
    Returns:
        MatchResult with score, reasons, detected skills, and red flags
    """
    score = 0.0
    reasons: List[str] = []
    skills_detected: List[str] = []
    red_flags: List[str] = []

    tech_score = 0.0
    location_score = 0.0
    seniority_score = 0.0
    experience_req_score = 0.0
    education_score = 0.0
    soft_score = 0.0
    industry_score = 0.0

    job_text_norm = _normalize_for_match(
        "\n".join(
            [
                job_offer.title or "",
                job_offer.company or "",
                job_offer.location or "",
                job_offer.raw_description or "",
            ]
        )
    )
    title_norm = _normalize_for_match(job_offer.title or "")
    
    # 1) Technical skills match (50 points max)
    candidate_tech = _dedupe_preserve_order(candidate.technical_skills or [])
    matched_tech: List[str] = []
    for skill in candidate_tech:
        if _contains_skill(job_text_norm, skill):
            matched_tech.append(skill)

    if candidate_tech:
        denom = max(1, min(12, len(candidate_tech)))
        tech_score = 50.0 * (min(len(matched_tech), denom) / denom)
        score += tech_score
        if matched_tech:
            skills_detected.extend(matched_tech)
            reasons.append(
                f"Tech: +{tech_score:.1f}/50 (match {len(matched_tech)}/{len(candidate_tech)}; cap denom={denom})"
            )
            reasons.append(f"Tech matchées: {', '.join(matched_tech[:20])}")
        else:
            red_flags.append("Aucune compétence technique du CV détectée dans l'offre")
    else:
        red_flags.append("Compétences techniques CV manquantes")
    
    # 2) Location preference (10 points max) - seulement si le candidat a des préférences
    if job_offer.location and candidate.preferred_locations:
        location_norm = _normalize_for_match(job_offer.location)
        for pref_location in candidate.preferred_locations:
            pref_norm = _normalize_for_match(pref_location)
            if pref_norm and (pref_norm in location_norm or "remote" in location_norm):
                location_score = 10.0
                score += location_score
                reasons.append(f"Localisation: +{location_score:.1f}/10 ({job_offer.location})")
                break
    
    # 3) Seniority + years requirement (20 points max)
    # - signaux dans le titre
    seniority_keywords: dict[str, int] = {
        "principal": 8,
        "staff": 7,
        "lead": 6,
        "senior": 5,
        "mid": 3,
        "junior": 1,
    }

    for keyword, years_required in seniority_keywords.items():
        if keyword in title_norm or keyword in job_text_norm:
            if candidate.years_of_experience >= years_required:
                seniority_score = 10.0
                score += seniority_score
                reasons.append(f"Séniorité: +{seniority_score:.1f}/10 ({keyword}, exp={candidate.years_of_experience})")
            else:
                red_flags.append(f"Séniorité potentiellement insuffisante pour '{keyword}'")
            break

    # - contrainte explicite "X+ years" / "X ans"
    m = re.search(r"\b(\d{1,2})\s*\+?\s*(?:years?|ans?)\b", job_text_norm)
    if m:
        required = int(m.group(1))
        if candidate.years_of_experience >= required:
            experience_req_score = 10.0
            score += experience_req_score
            reasons.append(f"Expérience: +{experience_req_score:.1f}/10 (≥ {required})")
        else:
            red_flags.append(f"Expérience requise: ≥ {required}")
    
    # 4) Education (5 points max) - only if both sides provide signal
    if re.search(r"\b(master|bachelor|phd|degree|licence|doctorat)\b", job_text_norm):
        if candidate.education_level:
            education_score = 5.0
            score += education_score
            reasons.append(f"Éducation: +{education_score:.1f}/5 (CV={candidate.education_level})")
        else:
            red_flags.append("Niveau d'études CV non détecté")
    
    # 5) Soft skills (15 points max) - basé sur les soft skills du CV
    candidate_soft = _dedupe_preserve_order(candidate.soft_skills or [])
    matched_soft: List[str] = []
    for soft in candidate_soft:
        if _contains_skill(job_text_norm, soft):
            matched_soft.append(soft)

    if candidate_soft:
        denom = max(1, min(8, len(candidate_soft)))
        soft_score = 15.0 * (min(len(matched_soft), denom) / denom)
        score += soft_score
        if matched_soft:
            reasons.append(f"Soft: +{soft_score:.1f}/15 (match {len(matched_soft)}/{len(candidate_soft)}; denom={denom})")
            reasons.append(f"Soft matchés: {', '.join(matched_soft[:12])}")
    else:
        # pas de malus, mais un signal utile
        red_flags.append("Soft skills CV manquants")
    
    # 6) Bonus: industrie (5 points max)
    for industry in candidate.industry_experience or []:
        if _normalize_for_match(industry) and _normalize_for_match(industry) in job_text_norm:
            industry_score = 5.0
            score += industry_score
            reasons.append(f"Industrie: +{industry_score:.1f}/5 ({industry})")
            break
    
    # 7) Red flags génériques (texte offre)
    red_flag_keywords = [
        ("on-site only", "Présence sur site obligatoire"),
        ("relocation required", "Relocation demandé"),
        ("security clearance", "Habilitation sécurité potentielle"),
        ("phd required", "PhD requis"),
    ]

    for keyword, flag_message in red_flag_keywords:
        if keyword in job_text_norm:
            red_flags.append(flag_message)
    
    # Cap score at 100
    score = min(100.0, score)
    
    # Format results
    if reasons:
        reasons.insert(
            0,
            " | ".join(
                [
                    f"Breakdown: tech={tech_score:.1f}/50",
                    f"soft={soft_score:.1f}/15",
                    f"loc={location_score:.1f}/10",
                    f"seniority={seniority_score:.1f}/10",
                    f"exp={experience_req_score:.1f}/10",
                    f"edu={education_score:.1f}/5",
                    f"industry={industry_score:.1f}/5",
                ]
            ),
        )

    reasons_text = "; ".join(reasons) if reasons else "Match calculé mais peu de signaux exploitables"
    skills_text = ", ".join(_dedupe_preserve_order(skills_detected)) if skills_detected else ""
    red_flags_text = "; ".join(_dedupe_preserve_order(red_flags)) if red_flags else ""
    
    return MatchResult(
        score=round(score, 2),
        reasons=reasons_text,
        skills_detected=skills_text,
        red_flags=red_flags_text
    )


def extract_profile_from_user(user) -> CandidateProfile:
    """
    Extract candidate profile from user data and CV.
    
    Args:
        user: User object with cv_file_path or cv_text
    
    Returns:
        CandidateProfile
    """
    # 1) Chemin prioritaire: sections CV déjà extraites et stockées sur l'utilisateur
    tech_text = getattr(user, "cv_technical_skills", None)
    soft_text = getattr(user, "cv_soft_skills", None)
    experience_text = getattr(user, "cv_experience", None)
    projects_text = getattr(user, "cv_projects", None)
    education_text = getattr(user, "cv_education", None)
    summary_text = getattr(user, "cv_summary", None)

    technical_skills = _dedupe_preserve_order(_iter_skill_candidates(tech_text or ""))
    soft_skills = _dedupe_preserve_order(_iter_skill_candidates(soft_text or ""))
    years = _infer_years_of_experience_from_text(experience_text, projects_text)
    education_level = _infer_education_level(education_text)

    # Title: si on ne sait pas inférer proprement, on laisse vide (évite un "default" fictif)
    title = ""
    if summary_text:
        first_line = summary_text.strip().splitlines()[0].strip()
        # Heuristique: une ligne courte et “titre-like”
        if 0 < len(first_line) <= 80 and len(first_line.split()) <= 10:
            title = first_line

    candidate = CandidateProfile(
        name=getattr(user, "name", ""),
        title=title,
        years_of_experience=years,
        technical_skills=technical_skills,
        soft_skills=soft_skills,
        languages=[],
        education_level=education_level,
        field_of_study="",
        preferred_locations=[],
        preferred_job_types=[],
        certifications=[],
        industry_experience=[],
    )

    # 2) Optionnel: enrichissement IA si dispo (sans retomber sur un profil hardcodé)
    from app.config import settings
    if getattr(user, "cv_text", None) and settings.openai_api_key:
        try:
            from app.services.cv_service import parse_cv_with_ai

            parsed_cv = parse_cv_with_ai(user.cv_text, settings.openai_api_key)
            if parsed_cv.get("parsed"):
                candidate.title = candidate.title or (parsed_cv.get("title") or "")
                candidate.education_level = candidate.education_level or (parsed_cv.get("education_level") or "")
                candidate.field_of_study = candidate.field_of_study or (parsed_cv.get("field_of_study") or "")
                if not candidate.technical_skills and parsed_cv.get("technical_skills"):
                    candidate.technical_skills = _dedupe_preserve_order(parsed_cv.get("technical_skills", []))
                if not candidate.soft_skills and parsed_cv.get("soft_skills"):
                    candidate.soft_skills = _dedupe_preserve_order(parsed_cv.get("soft_skills", []))
        except Exception as e:
            logger.warning("cv_ai_enrichment_failed", extra={"error": str(e)})

    return candidate


def calculate_job_match(job_offer_id: int, user_id: int, db) -> 'JobMatch':
    """
    Calculate and save job match for a job offer using user's profile.
    
    Args:
        job_offer_id: The job offer ID
        user_id: The user ID (for CV and profile)
        db: Database session
    
    Returns:
        JobMatch object
    """
    from app.crud import job_offer as job_offer_crud
    from app.crud import job_match as job_match_crud
    from app.crud import user as user_crud
    from app.schemas.job_match import JobMatchCreate
    
    # Get job offer with user_id filter
    job_offer = job_offer_crud.get(db, job_offer_id, user_id)
    if not job_offer:
        raise ValueError(f"Job offer {job_offer_id} not found")
    
    # Get user and extract profile
    user = user_crud.get(db, user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")
    
    candidate_profile = extract_profile_from_user(user)
    
    # Compute match with user's profile
    match_result = compute_match_score(job_offer, candidate_profile)
    
    # Create job match in database with user_id
    job_match_data = JobMatchCreate(
        job_offer_id=job_offer_id,
        score=match_result.score,
        reasons=match_result.reasons,
        skills_detected=match_result.skills_detected,
        red_flags=match_result.red_flags
    )
    
    job_match = job_match_crud.create(db, job_match_data, user_id)
    return job_match
