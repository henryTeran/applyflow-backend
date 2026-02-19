#!/usr/bin/env python3
"""
Script de test des endpoints pour vérifier la conformité avec le frontend.
"""

def check_endpoints():
    """Vérifie que tous les endpoints nécessaires existent."""
    print("🔍 Vérification des endpoints API...\n")
    
    from app.api.v1 import drafts, job_matches, job_offers, applications
    import inspect
    
    results = []
    
    # 1. Vérifier endpoint send draft
    print("1️⃣  Endpoint POST /drafts/{draft_id}/send")
    has_send = hasattr(drafts, 'send_draft')
    if has_send:
        sig = inspect.signature(drafts.send_draft)
        params = list(sig.parameters.keys())
        has_user = 'current_user' in params
        has_db = 'db' in params
        has_draft_id = 'draft_id' in params
        
        if has_user and has_db and has_draft_id:
            print("   ✅ Endpoint existe avec current_user")
            results.append(("send_draft", True))
        else:
            print("   ❌ Endpoint existe mais paramètres manquants")
            results.append(("send_draft", False))
    else:
        print("   ❌ Endpoint manquant")
        results.append(("send_draft", False))
    
    # 2. Vérifier filtrage user_id dans list_job_offers
    print("\n2️⃣  Filtrage user_id dans /job-offers/")
    try:
        import ast
        import inspect
        source = inspect.getsource(job_offers.list_job_offers)
        has_current_user = 'current_user' in source
        has_user_id_filter = 'user_id=current_user.id' in source
        
        if has_current_user and has_user_id_filter:
            print("   ✅ Filtre par current_user.id présent")
            results.append(("filter_job_offers", True))
        else:
            print("   ❌ Filtrage manquant")
            results.append(("filter_job_offers", False))
    except Exception as e:
        print(f"   ⚠️  Impossible de vérifier: {e}")
        results.append(("filter_job_offers", False))
    
    # 3. Vérifier filtrage dans list_applications
    print("\n3️⃣  Filtrage user_id dans /applications/")
    try:
        source = inspect.getsource(applications.list_applications)
        has_current_user = 'current_user' in source
        has_user_id_filter = 'user_id=current_user.id' in source
        
        if has_current_user and has_user_id_filter:
            print("   ✅ Filtre par current_user.id présent")
            results.append(("filter_applications", True))
        else:
            print("   ❌ Filtrage manquant")
            results.append(("filter_applications", False))
    except Exception as e:
        print(f"   ⚠️  Impossible de vérifier: {e}")
        results.append(("filter_applications", False))
    
    # 4. Vérifier message d'erreur CV dans analyze
    print("\n4️⃣  Vérification CV dans /job-matches/analyze/")
    try:
        source = inspect.getsource(job_matches.analyze_job_match)
        has_cv_check = 'cv_file_path' in source or 'cv_text' in source
        has_upload_message = 'upload' in source.lower() and 'cv' in source.lower()
        has_400_error = '400' in source
        
        if has_cv_check and has_upload_message and has_400_error:
            print("   ✅ Vérification CV avec erreur 400 explicite")
            results.append(("cv_check_analyze", True))
        else:
            print("   ❌ Vérification CV manquante ou incorrecte")
            results.append(("cv_check_analyze", False))
    except Exception as e:
        print(f"   ⚠️  Impossible de vérifier: {e}")
        results.append(("cv_check_analyze", False))
    
    # 5. Vérifier message d'erreur CV dans generate_draft
    print("\n5️⃣  Vérification CV dans /drafts/generate/")
    try:
        source = inspect.getsource(drafts.generate_draft)
        has_cv_check = 'cv_file_path' in source or 'cv_text' in source
        has_upload_message = 'upload' in source.lower() and 'cv' in source.lower()
        has_400_error = '400' in source
        
        if has_cv_check and has_upload_message and has_400_error:
            print("   ✅ Vérification CV avec erreur 400 explicite")
            results.append(("cv_check_generate", True))
        else:
            print("   ❌ Vérification CV manquante ou incorrecte")
            results.append(("cv_check_generate", False))
    except Exception as e:
        print(f"   ⚠️  Impossible de vérifier: {e}")
        results.append(("cv_check_generate", False))
    
    # Résumé
    print("\n" + "="*60)
    print("📊 RÉSUMÉ")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n{passed}/{total} vérifications réussies")
    
    if passed == total:
        print("\n🎉 TOUS LES POINTS FRONTEND SONT CONFORMES !")
        return 0
    else:
        print("\n⚠️  Certains points nécessitent attention")
        return 1


if __name__ == "__main__":
    import sys
    try:
        sys.exit(check_endpoints())
    except Exception as e:
        print(f"\n❌ Erreur lors de la vérification: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
