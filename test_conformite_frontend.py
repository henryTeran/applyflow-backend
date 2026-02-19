#!/usr/bin/env python3
"""
Script de test rapide pour vérifier la conformité backend/frontend.
Teste tous les champs et endpoints mentionnés dans l'analyse frontend.
"""

import sys
import os

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.job_offer import JobOffer
from app.models.application_draft import ApplicationDraft
from app.models.user import User


def test_field_existence(model, field_name):
    """Vérifie qu'un champ existe dans un modèle SQLAlchemy"""
    if hasattr(model, field_name):
        column = getattr(model, field_name)
        print(f"  ✅ {model.__name__}.{field_name} existe")
        return True
    else:
        print(f"  ❌ {model.__name__}.{field_name} MANQUANT")
        return False


def main():
    print("=" * 70)
    print("🧪 VÉRIFICATION CONFORMITÉ BACKEND/FRONTEND")
    print("=" * 70)
    print()
    
    all_passed = True
    
    # ========== TEST 1: Champs JobOffer ==========
    print("📋 TEST 1: Champs JobOffer")
    print("-" * 70)
    
    job_offer_fields = [
        "source",
        "application_type",
        "application_url",
        "raw_description"  # ⚠️ Nom critique
    ]
    
    for field in job_offer_fields:
        if not test_field_existence(JobOffer, field):
            all_passed = False
    
    # Vérifier que "description" n'existe PAS (devrait être raw_description)
    if hasattr(JobOffer, "description"):
        print(f"  ⚠️ JobOffer.description existe (devrait être raw_description)")
        all_passed = False
    else:
        print(f"  ✅ JobOffer.description n'existe pas (correct, on utilise raw_description)")
    
    print()
    
    # ========== TEST 2: Champs ApplicationDraft ==========
    print("📋 TEST 2: Champs ApplicationDraft")
    print("-" * 70)
    
    draft_fields = [
        "cover_letter_text",  # ⚠️ Nom critique (pas cover_letter_content)
        "email_subject",
        "email_body"
    ]
    
    for field in draft_fields:
        if not test_field_existence(ApplicationDraft, field):
            all_passed = False
    
    # Vérifier que "cover_letter_content" n'existe PAS
    if hasattr(ApplicationDraft, "cover_letter_content"):
        print(f"  ⚠️ ApplicationDraft.cover_letter_content existe (devrait être cover_letter_text)")
        all_passed = False
    else:
        print(f"  ✅ ApplicationDraft.cover_letter_content n'existe pas (correct, on utilise cover_letter_text)")
    
    print()
    
    # ========== TEST 3: Champ User ==========
    print("📋 TEST 3: Champ User")
    print("-" * 70)
    
    if not test_field_existence(User, "cover_letter_template"):
        all_passed = False
    
    print()
    
    # ========== TEST 4: Endpoint Scraping ==========
    print("📋 TEST 4: Endpoint Scraping")
    print("-" * 70)
    
    # Chemin absolu vers le fichier
    current_dir = os.path.dirname(os.path.abspath(__file__))
    scraping_service_path = os.path.join(current_dir, "app", "services", "scraping_service.py")
    
    if os.path.exists(scraping_service_path):
        print(f"  ✅ app/services/scraping_service.py existe")
        
        # Vérifier que les fonctions de scraping existent
        with open(scraping_service_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            if "def scrape_linkedin" in content:
                print(f"  ✅ Fonction scrape_linkedin() trouvée")
            else:
                print(f"  ❌ Fonction scrape_linkedin() MANQUANTE")
                all_passed = False
            
            if "def scrape_indeed" in content:
                print(f"  ✅ Fonction scrape_indeed() trouvée")
            else:
                print(f"  ❌ Fonction scrape_indeed() MANQUANTE")
                all_passed = False
            
            if "def scrape_wttj" in content:
                print(f"  ✅ Fonction scrape_wttj() trouvée")
            else:
                print(f"  ❌ Fonction scrape_wttj() MANQUANTE")
                all_passed = False
            
            if "class ScrapeResult" in content:
                print(f"  ✅ Classe ScrapeResult trouvée")
            else:
                print(f"  ❌ Classe ScrapeResult MANQUANTE")
                all_passed = False
    else:
        print(f"  ❌ app/services/scraping_service.py MANQUANT")
        all_passed = False
    
    # Vérifier l'endpoint dans job_offers.py
    job_offers_api_path = os.path.join(current_dir, "app", "api", "v1", "job_offers.py")
    
    if os.path.exists(job_offers_api_path):
        with open(job_offers_api_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            if '@router.post("/scrape"' in content:
                print(f"  ✅ Endpoint POST /scrape trouvé dans job_offers.py")
            else:
                print(f"  ❌ Endpoint POST /scrape MANQUANT dans job_offers.py")
                all_passed = False
    
    print()
    
    # ========== TEST 5: Dépendances Selenium ==========
    print("📋 TEST 5: Dépendances Selenium")
    print("-" * 70)
    
    requirements_path = os.path.join(current_dir, "requirements.txt")
    
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            if "selenium" in content:
                print(f"  ✅ selenium trouvé dans requirements.txt")
            else:
                print(f"  ⚠️ selenium MANQUANT dans requirements.txt")
                print(f"     Ajouter: selenium==4.16.0")
            
            if "webdriver-manager" in content:
                print(f"  ✅ webdriver-manager trouvé dans requirements.txt")
            else:
                print(f"  ⚠️ webdriver-manager MANQUANT dans requirements.txt")
                print(f"     Ajouter: webdriver-manager==4.0.1")
    
    # Vérifier si Selenium est installé
    try:
        import selenium
        print(f"  ✅ selenium installé (version {selenium.__version__})")
    except ImportError:
        print(f"  ⚠️ selenium non installé")
        print(f"     Exécuter: pip install selenium webdriver-manager")
    
    try:
        import webdriver_manager
        print(f"  ✅ webdriver-manager installé")
    except ImportError:
        print(f"  ⚠️ webdriver-manager non installé")
        print(f"     Exécuter: pip install selenium webdriver-manager")
    
    print()
    
    # ========== RÉSULTAT FINAL ==========
    print("=" * 70)
    if all_passed:
        print("✅ SUCCÈS: Backend 100% conforme aux attentes du frontend !")
        print()
        print("🚀 Le frontend peut commencer l'intégration immédiatement.")
        print()
        print("📚 Voir REPONSE_ANALYSE_FRONTEND.md pour les détails complets.")
        print("=" * 70)
        return 0
    else:
        print("❌ ÉCHEC: Certaines vérifications ont échoué.")
        print()
        print("⚠️ Voir les erreurs ci-dessus pour corriger.")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
