#!/usr/bin/env python3
"""
Script de validation de la migration multi-utilisateur.
Vérifie que tous les imports et configurations sont corrects.
"""

import sys
import traceback

def test_imports():
    """Test que tous les modules s'importent correctement."""
    print("🔍 Test des imports...")
    
    try:
        # Models
        from app.models.user import User
        from app.models.job_offer import JobOffer
        from app.models.job_match import JobMatch
        from app.models.application_draft import ApplicationDraft
        from app.models.application import Application
        from app.models.timeline_event import TimelineEvent
        print("  ✅ Models importés")
        
        # Vérifier que les modèles ont user_id
        assert hasattr(JobOffer, 'user_id'), "JobOffer n'a pas user_id"
        assert hasattr(JobMatch, 'user_id'), "JobMatch n'a pas user_id"
        assert hasattr(ApplicationDraft, 'user_id'), "ApplicationDraft n'a pas user_id"
        assert hasattr(Application, 'user_id'), "Application n'a pas user_id"
        assert hasattr(TimelineEvent, 'user_id'), "TimelineEvent n'a pas user_id"
        print("  ✅ Tous les modèles ont user_id")
        
        # CRUD
        from app.crud import job_offer, job_match, application_draft, application, timeline_event
        print("  ✅ CRUD importés")
        
        # Services
        from app.services.match_service import calculate_job_match
        from app.services.draft_service import generate_application_draft
        print("  ✅ Services importés")
        
        # API
        from app.api.v1 import job_offers, job_matches, drafts, applications, timeline
        print("  ✅ Endpoints API importés")
        
        # Agent
        from app.agents.pipeline_agent import run_job_offer_pipeline
        print("  ✅ Pipeline agent importé")
        
        # App principale
        from app.main import app
        print("  ✅ Application FastAPI importée")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur d'import: {e}")
        traceback.print_exc()
        return False


def test_signatures():
    """Vérifie que les signatures des fonctions sont correctes."""
    print("\n🔍 Test des signatures de fonctions...")
    
    try:
        from app.crud import job_offer as job_offer_crud
        from app.services.match_service import calculate_job_match
        from app.services.draft_service import generate_application_draft
        from app.agents.pipeline_agent import run_job_offer_pipeline
        import inspect
        
        # Test CRUD signatures
        sig = inspect.signature(job_offer_crud.create)
        params = list(sig.parameters.keys())
        assert 'user_id' in params, "job_offer.create n'a pas user_id"
        print("  ✅ job_offer.create(db, job_offer, user_id)")
        
        sig = inspect.signature(job_offer_crud.list_job_offers)
        params = list(sig.parameters.keys())
        assert 'user_id' in params, "job_offer.list_job_offers n'a pas user_id"
        print("  ✅ job_offer.list_job_offers(db, user_id, ...)")
        
        # Test service signatures
        sig = inspect.signature(calculate_job_match)
        params = list(sig.parameters.keys())
        assert 'user_id' in params, "calculate_job_match n'a pas user_id"
        print("  ✅ calculate_job_match(job_offer_id, user_id, db)")
        
        sig = inspect.signature(generate_application_draft)
        params = list(sig.parameters.keys())
        assert 'user_id' in params, "generate_application_draft n'a pas user_id"
        print("  ✅ generate_application_draft(job_offer_id, user_id, db)")
        
        # Test pipeline signature
        sig = inspect.signature(run_job_offer_pipeline)
        params = list(sig.parameters.keys())
        assert 'user_id' in params, "run_job_offer_pipeline n'a pas user_id"
        print("  ✅ run_job_offer_pipeline(job_offer_id, user_id, db, regenerate)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur de signature: {e}")
        traceback.print_exc()
        return False


def test_database_schema():
    """Vérifie le schéma de la base de données."""
    print("\n🔍 Test du schéma de base de données...")
    
    try:
        from app.database import engine
        from sqlalchemy import inspect as sql_inspect
        
        inspector = sql_inspect(engine)
        
        # Tables à vérifier
        tables_to_check = [
            'job_offers',
            'job_matches', 
            'application_drafts',
            'applications',
            'timeline_events'
        ]
        
        for table in tables_to_check:
            columns = [col['name'] for col in inspector.get_columns(table)]
            assert 'user_id' in columns, f"{table} n'a pas la colonne user_id"
            print(f"  ✅ {table} a user_id")
            
            # Vérifier les FK
            fks = inspector.get_foreign_keys(table)
            user_fk = [fk for fk in fks if 'user_id' in fk['constrained_columns']]
            assert len(user_fk) > 0, f"{table} n'a pas de FK vers users"
            print(f"  ✅ {table} a FK vers users")
            
            # Vérifier les index
            indexes = inspector.get_indexes(table)
            user_index = [idx for idx in indexes if 'user_id' in idx['column_names']]
            assert len(user_index) > 0, f"{table} n'a pas d'index sur user_id"
            print(f"  ✅ {table} a index sur user_id")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur de schéma: {e}")
        traceback.print_exc()
        return False


def main():
    """Exécute tous les tests de validation."""
    print("=" * 60)
    print("🚀 VALIDATION DE LA MIGRATION MULTI-UTILISATEUR")
    print("=" * 60)
    
    results = []
    
    # Test 1: Imports
    results.append(("Imports", test_imports()))
    
    # Test 2: Signatures
    results.append(("Signatures", test_signatures()))
    
    # Test 3: Database schema
    results.append(("Schéma DB", test_database_schema()))
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ")
    print("=" * 60)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(success for _, success in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 TOUTES LES VALIDATIONS ONT RÉUSSI !")
        print("   La migration multi-utilisateur est complète et fonctionnelle.")
        print("\n💡 Prochaines étapes:")
        print("   1. Lancer le serveur: uvicorn app.main:app --reload --port 8000")
        print("   2. Tester manuellement avec 2 utilisateurs")
        print("   3. Mettre à jour les tests unitaires")
        return 0
    else:
        print("⚠️  CERTAINES VALIDATIONS ONT ÉCHOUÉ")
        print("   Vérifier les erreurs ci-dessus")
        return 1


if __name__ == "__main__":
    sys.exit(main())
