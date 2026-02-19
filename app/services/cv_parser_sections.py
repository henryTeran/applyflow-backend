"""CV section extraction service.

Objectif:
- Normaliser d'abord le texte avec des marqueurs uniques: === SECTION ===
- Extraire 8 sections: personal_info, summary, it_skills, soft_skills, experience,
  projects, education, awards
- Gérer les titres collés (ex: "SOFT SKILLS IT SKILLS")
- Réassocier les dates orphelines de PROJECTS (si nb dates == nb projets, associer dans l'ordre)

Note: pour compatibilité avec l'existant, la clé "technical_skills" est aussi renvoyée
comme alias de "it_skills".
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

logger = logging.getLogger(__name__)


_PAGE_BREAK_RE = re.compile(r"---\s*PAGE\s*BREAK\s*---", re.IGNORECASE)


def _cleanup_block(text: str) -> str:
    text = _PAGE_BREAK_RE.sub("", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Trim every line but keep line breaks
    text = "\n".join(line.strip() for line in text.splitlines())
    return text.strip()


@dataclass(frozen=True)
class _SectionDef:
    marker: str
    output_key: str
    header_patterns: Tuple[re.Pattern[str], ...]


def _compile_headers(phrases: Sequence[str]) -> Tuple[re.Pattern[str], ...]:
    # Word-boundary-ish matching. Allow separators like ':' and excessive spaces.
    compiled: List[re.Pattern[str]] = []
    for phrase in phrases:
        # e.g. "IT SKILLS" -> r"\bIT\s+SKILLS\b"
        tokens = [re.escape(t) for t in phrase.split()]
        pat = r"\b" + r"\s+".join(tokens) + r"\b"
        compiled.append(re.compile(pat, re.IGNORECASE))
    return tuple(compiled)


_SECTIONS: Tuple[_SectionDef, ...] = (
    _SectionDef(
        marker="SUMMARY",
        output_key="summary",
        header_patterns=_compile_headers(
            [
                "SUMMARY",
                "PROFESSIONAL SUMMARY",
                "PROFILE",
                "PROFESSIONAL PROFILE",
                "ABOUT ME",
            ]
        ),
    ),
    _SectionDef(
        marker="SOFT SKILLS",
        output_key="soft_skills",
        header_patterns=_compile_headers(["SOFT SKILLS", "SOFT-SKILLS", "COMPETENCIES", "COMPETENCES"]),
    ),
    _SectionDef(
        marker="IT SKILLS",
        output_key="it_skills",
        header_patterns=_compile_headers(
            [
                "IT SKILLS",
                "TECHNICAL SKILLS",
                "TECH SKILLS",
                "TECHNICAL COMPETENCIES",
            ]
        ),
    ),
    _SectionDef(
        marker="EXPERIENCE",
        output_key="experience",
        header_patterns=_compile_headers(["EXPERIENCE", "WORK EXPERIENCE", "PROFESSIONAL EXPERIENCE"]),
    ),
    _SectionDef(
        marker="PROJECTS",
        output_key="projects",
        header_patterns=_compile_headers(["PROJECTS", "PROJECT", "PROJECT EXPERIENCE"]),
    ),
    _SectionDef(
        marker="EDUCATION",
        output_key="education",
        header_patterns=_compile_headers(["EDUCATION", "ACADEMIC BACKGROUND", "STUDIES"]),
    ),
    _SectionDef(
        marker="AWARDS",
        output_key="awards",
        header_patterns=_compile_headers(["AWARDS", "AWARD S", "AWARD", "CERTIFICATIONS", "CERTIFICATION"]),
    ),
)


def _split_personal_and_summary(personal_text: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """Heuristic split when SUMMARY/PROFILE header is missing.

    Many PDFs include a long profile paragraph directly after contact lines.
    We keep early short lines as personal_info and move the first long sentence-like
    paragraph to summary.
    """
    if not personal_text:
        return None, None

    lines = [ln.strip() for ln in personal_text.splitlines()]
    lines = [ln for ln in lines if ln]
    if len(lines) < 6:
        return personal_text.strip() or None, None

    start_idx: Optional[int] = None
    for i, ln in enumerate(lines):
        if len(ln) >= 80 and ("." in ln or ";" in ln):
            start_idx = i
            break

    if start_idx is None or start_idx <= 1:
        return personal_text.strip() or None, None

    personal_part = "\n".join(lines[:start_idx]).strip() or None
    summary_part = "\n".join(lines[start_idx:]).strip() or None
    return personal_part, summary_part


def _all_header_phrases() -> List[str]:
    # For glued-title splitting: we want full phrases, longest first.
    # Explicit list (longest first) – keeps behavior deterministic.
    phrases: List[str] = [
        "PROFESSIONAL SUMMARY",
        "PROFESSIONAL PROFILE",
        "WORK EXPERIENCE",
        "PROFESSIONAL EXPERIENCE",
        "TECHNICAL COMPETENCIES",
        "TECHNICAL SKILLS",
        "SOFT SKILLS",
        "IT SKILLS",
        "PROJECT EXPERIENCE",
        "PROJECTS",
        "EDUCATION",
        "ACADEMIC BACKGROUND",
        "CERTIFICATIONS",
        "AWARDS",
        "SUMMARY",
        "PROFILE",
        "ABOUT ME",
        "COMPETENCIES",
        "COMPETENCES",
        "STUDIES",
    ]
    phrases.sort(key=len, reverse=True)
    return phrases


_HEADER_PHRASES = _all_header_phrases()


def _split_glued_headers(line: str) -> List[str]:
    """Split a line that contains multiple headers, e.g. "SOFT SKILLS IT SKILLS".

    Returns a list of sub-lines (order preserved).
    """
    raw = re.sub(r"\s+", " ", line).strip()
    if not raw:
        return [""]

    upper = raw.upper()
    hits: List[Tuple[int, int]] = []
    for phrase in _HEADER_PHRASES:
        idx = upper.find(phrase)
        if idx != -1:
            hits.append((idx, idx + len(phrase)))

    # Need at least two distinct header occurrences to justify splitting.
    if len(hits) < 2:
        return [raw]

    # Sort and remove overlaps.
    hits.sort()
    non_overlapping: List[Tuple[int, int]] = []
    last_end = -1
    for start, end in hits:
        if start >= last_end:
            non_overlapping.append((start, end))
            last_end = end

    if len(non_overlapping) < 2:
        return [raw]

    # If the line is basically just headers, split them onto separate lines.
    # Otherwise, keep as-is (safer for content lines that happen to contain words).
    remainder = raw
    for phrase in _HEADER_PHRASES:
        remainder = re.sub(rf"\b{re.escape(phrase)}\b", "", remainder, flags=re.IGNORECASE)
    remainder = re.sub(r"[\s:|/\-–—]+", "", remainder)
    if remainder:
        return [raw]

    parts: List[str] = []
    for start, end in non_overlapping:
        parts.append(raw[start:end].strip())
    return parts


def _insert_newlines_before_headers(line: str) -> str:
    """Insert newlines before known headers even if they are appended to a content line.

    Example:
    "... PCB boards SOFT SKILLS IT SKILLS" -> "... PCB boards\nSOFT SKILLS IT SKILLS"
    """
    out = line
    for phrase in _HEADER_PHRASES:
        # Only split if the phrase is preceded by some non-space text.
        pattern = re.compile(rf"(?i)(?<=\S)\s+({re.escape(phrase)})(?=\s|$)")
        out = pattern.sub(r"\n\1", out)
    return out


def _match_header(line: str) -> Optional[_SectionDef]:
    candidate = line.strip().strip(":").strip()
    if not candidate:
        return None
    for sec in _SECTIONS:
        for pat in sec.header_patterns:
            # Match whole line (header only) or header at beginning followed by ':' or spaces.
            if pat.fullmatch(candidate) or re.match(pat.pattern + r"(?:\s*:.*)?$", candidate, re.IGNORECASE):
                return sec
    return None


def normalize_sections_with_markers(cv_text: str) -> str:
    """Normalize CV text by inserting unique section markers: === SECTION ===."""
    text = cv_text or ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _PAGE_BREAK_RE.sub("\n--- PAGE BREAK ---\n", text)

    out_lines: List[str] = []
    for raw_line in text.split("\n"):
        # Preserve empty lines
        if not raw_line.strip():
            out_lines.append("")
            continue

        # 1) normalize whitespace
        line = re.sub(r"[\t ]+", " ", raw_line).strip()
        # 2) split inline headers (header appended to a content line)
        line = _insert_newlines_before_headers(line)
        # 3) split glued titles safely
        for chunk in line.split("\n"):
            for sub in _split_glued_headers(chunk):
                sec = _match_header(sub)
                if sec is None:
                    out_lines.append(sub)
                    continue
                out_lines.append("")
                out_lines.append(f"=== {sec.marker} ===")
                out_lines.append("")

    normalized = "\n".join(out_lines)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip()


_MARKER_LINE_RE = re.compile(r"(?m)^===\s*([A-Z0-9 _-]+?)\s*===$")


def _extract_by_markers(normalized_text: str) -> Dict[str, Optional[str]]:
    # Map marker -> output_key
    marker_to_key: Dict[str, str] = {sec.marker: sec.output_key for sec in _SECTIONS}

    matches = list(_MARKER_LINE_RE.finditer(normalized_text))
    blocks: Dict[str, str] = {}

    if not matches:
        # No markers found => treat everything as personal_info.
        cleaned = _cleanup_block(normalized_text)
        return {
            "personal_info": cleaned or None,
            "summary": None,
            "it_skills": None,
            "soft_skills": None,
            "experience": None,
            "projects": None,
            "education": None,
            "awards": None,
        }

    # personal info = text before first marker
    first_start = matches[0].start()
    personal = _cleanup_block(normalized_text[:first_start])

    for idx, m in enumerate(matches):
        marker_raw = m.group(1).strip().upper()
        # Normalize marker name
        marker = re.sub(r"\s+", " ", marker_raw)
        content_start = m.end()
        content_end = matches[idx + 1].start() if idx + 1 < len(matches) else len(normalized_text)
        content = _cleanup_block(normalized_text[content_start:content_end])
        if marker in marker_to_key and content:
            blocks[marker_to_key[marker]] = content

    return {
        "personal_info": personal or None,
        "summary": blocks.get("summary"),
        "it_skills": blocks.get("it_skills"),
        "soft_skills": blocks.get("soft_skills"),
        "experience": blocks.get("experience"),
        "projects": blocks.get("projects"),
        "education": blocks.get("education"),
        "awards": blocks.get("awards"),
    }


# Date range: tries to match common CV formats.
_MONTH_YEAR = r"(?:0?[1-9]|1[0-2])\s*[\/\-.]\s*\d{4}"
_YEAR_MONTH = r"\d{4}\s*[\/\-.]\s*(?:0?[1-9]|1[0-2])"
_YEAR = r"\d{4}"
_DATE_EDGE = rf"(?:{_MONTH_YEAR}|{_YEAR_MONTH}|{_YEAR})"
_RANGE_SEP = r"(?:–|—|-|−|â€“|â€”|\u2013|\u2014)"
_DATE_RANGE_RE = re.compile(
    rf"{_DATE_EDGE}\s*{_RANGE_SEP}\s*(?:{_DATE_EDGE}|(?:PRESENT|TODAY|AUJOURD\s*HUI))",
    re.IGNORECASE,
)


_TECH_CUE_RE = re.compile(
    r"(?im)^(frontend|backend|full-?stack|devops|tools|databases?|testing|api|automation|cloud)\b"
)


def _split_soft_and_it_from_combined(it_skills_text: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """If SOFT SKILLS and IT SKILLS were merged, split using technical cue headings."""
    if not it_skills_text:
        return None, None

    lines = it_skills_text.splitlines()
    cut_idx: Optional[int] = None
    for i, ln in enumerate(lines):
        if _TECH_CUE_RE.search(ln.strip()):
            cut_idx = i
            break

    if cut_idx is None or cut_idx == 0:
        return None, it_skills_text.strip() or None

    soft = _cleanup_block("\n".join(lines[:cut_idx]))
    it_part = _cleanup_block("\n".join(lines[cut_idx:]))
    return (soft or None), (it_part or None)


def _extract_trailing_orphan_dates(projects_text: str) -> Tuple[str, List[str]]:
    lines = [ln.rstrip() for ln in projects_text.splitlines()]
    orphan_dates: List[str] = []

    i = len(lines) - 1
    while i >= 0:
        line = lines[i].strip()
        if not line:
            i -= 1
            continue

        found = [m.group(0).strip() for m in _DATE_RANGE_RE.finditer(line)]
        if not found:
            break

        # Consider this line orphan-only if removing found dates + separators leaves nothing.
        tmp = line
        for d in found:
            tmp = re.sub(re.escape(d), "", tmp, flags=re.IGNORECASE)
        tmp = re.sub(r"[\s,;|/\-–—]+", "", tmp)
        if tmp:
            # If the line ends with a date range, split off the trailing date as orphan.
            last = found[-1]
            if re.search(rf"{re.escape(last)}\s*$", line, flags=re.IGNORECASE):
                orphan_dates[0:0] = [last]
                lines[i] = re.sub(rf"\s*{re.escape(last)}\s*$", "", line, flags=re.IGNORECASE).rstrip()
                i -= 1
                continue
            break

        orphan_dates[0:0] = found  # prepend to keep original order
        i -= 1

    remaining = "\n".join(lines[: i + 1]).strip()
    return remaining, orphan_dates


def _split_project_blocks(projects_body: str) -> List[str]:
    body = _cleanup_block(projects_body)
    if not body:
        return []

    blocks = [b.strip() for b in re.split(r"\n{2,}", body) if b.strip()]
    if len(blocks) >= 2:
        return blocks

    # Fallback: split on typical "Title – ..." lines (consume the title line to avoid empty-match split issues)
    title_sep = r"(?:–|—|-|−|â€“|â€”|\u2013|\u2014)"
    title_line_re = re.compile(rf"(?m)^[A-Z][A-Za-z0-9 &/()]{{2,60}}\s*{title_sep}\s+.*$")
    starts = [m.start() for m in title_line_re.finditer(body)]
    if len(starts) >= 2:
        chunks: List[str] = []
        for i, start in enumerate(starts):
            end = starts[i + 1] if i + 1 < len(starts) else len(body)
            chunk = body[start:end].strip()
            if chunk:
                chunks.append(chunk)
        if len(chunks) >= 2:
            return chunks

    return blocks


def _reassociate_project_dates(projects_text: str) -> str:
    if not projects_text:
        return projects_text

    body, orphan_dates = _extract_trailing_orphan_dates(projects_text)
    if not orphan_dates:
        return projects_text

    blocks = _split_project_blocks(body)
    if not blocks:
        return projects_text

    if len(orphan_dates) != len(blocks):
        logger.debug(
            "PROJECTS: orphan dates found but count mismatch (dates=%s, projects=%s)",
            len(orphan_dates),
            len(blocks),
        )
        return projects_text

    reassociated: List[str] = []
    for project_block, date in zip(blocks, orphan_dates):
        if _DATE_RANGE_RE.search(project_block):
            reassociated.append(project_block)
        else:
            reassociated.append(f"[{date}]\n{project_block}")

    result = "\n\n".join(reassociated).strip()
    logger.info("PROJECTS: reassociated %s orphan date ranges", len(orphan_dates))
    return result


def extract_cv_sections(cv_text: str) -> dict:
    """Extract CV sections.

    Output keys (requested):
    - personal_info, summary, it_skills, soft_skills, experience, projects, education, awards

    Compatibility:
    - technical_skills is provided as alias of it_skills.
    """
    if not cv_text:
        logger.warning("No CV text provided")
        return {
            "personal_info": None,
            "summary": None,
            "it_skills": None,
            "technical_skills": None,
            "soft_skills": None,
            "experience": None,
            "projects": None,
            "education": None,
            "awards": None,
        }

    normalized = normalize_sections_with_markers(cv_text)
    sections = _extract_by_markers(normalized)

    # Fallback: if summary wasn't identified via header, try to split it out of personal_info.
    if not sections.get("summary") and sections.get("personal_info"):
        personal, summary = _split_personal_and_summary(sections.get("personal_info"))
        sections["personal_info"] = personal
        sections["summary"] = summary

    # If SOFT SKILLS header was glued with IT SKILLS, content often starts after IT marker.
    if not sections.get("soft_skills") and sections.get("it_skills"):
        soft, it_part = _split_soft_and_it_from_combined(sections.get("it_skills"))
        if soft and it_part:
            sections["soft_skills"] = soft
            sections["it_skills"] = it_part

    # Post-process PROJECTS for orphan-date reassociation
    if sections.get("projects"):
        sections["projects"] = _reassociate_project_dates(sections["projects"] or "") or None

    # Alias for backward compatibility
    sections["technical_skills"] = sections.get("it_skills")

    found = sum(1 for k, v in sections.items() if k != "technical_skills" and v)
    logger.info("Extracted CV sections: %s/8 sections found", found)
    logger.debug("Normalized markers preview: %s", normalized[:500])
    return sections
