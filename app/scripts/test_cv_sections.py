from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from app.services.cv_parser_sections import extract_cv_sections, normalize_sections_with_markers


logger = logging.getLogger(__name__)


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s %(name)s: %(message)s")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Charge un texte CV brut et affiche les sections extraites en JSON."
    )
    parser.add_argument(
        "path",
        type=Path,
        help="Chemin vers un fichier texte (ex: backend/cv_raw_text.txt)",
    )
    parser.add_argument(
        "--show-normalized",
        action="store_true",
        help="Affiche aussi la version normalisée avec marqueurs === SECTION ===.",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Logs en DEBUG")
    args = parser.parse_args()

    _configure_logging(args.verbose)

    if not args.path.exists():
        logger.error("Fichier introuvable: %s", args.path)
        return 2

    raw_text = args.path.read_text(encoding="utf-8", errors="replace")
    if args.show_normalized:
        normalized = normalize_sections_with_markers(raw_text)
        print("\n===== NORMALIZED =====\n")
        print(normalized)

    sections = extract_cv_sections(raw_text)
    print("\n===== SECTIONS JSON =====\n")
    print(json.dumps(sections, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
