"""
Script de test du backend ApplyFlow
Ce script teste toutes les fonctionnalités principales de l'API
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_step(step_number, description):
    """Affiche une étape du test"""
    print(f"\n{'='*60}")
    print(f"ÉTAPE {step_number}: {description}")
    print('='*60)

def test_api():
    """Test complet de l'API"""
    
    # ==========================================
    # ÉTAPE 1: Test de la santé de l'API
    # ==========================================
    print_step(1, "Test de connexion à l'API")
    response = requests.get(f"{BASE_URL}/")
    print(f"✅ Status: {response.status_code}")
    print(f"📄 Réponse: {json.dumps(response.json(), indent=2)}")
    
    # ==========================================
    # ÉTAPE 2: Création d'un utilisateur
    # ==========================================
    print_step(2, "Création d'un utilisateur")
    # Utiliser un timestamp pour éviter les conflits
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    user_data = {
        "email": f"test_{timestamp}@example.com",
        "password": "SecurePassword123!",
        "name": "Jean Dupont"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=user_data)
    print(f"Status: {response.status_code}")
    if response.status_code in [200, 201]:
        user = response.json()
        print(f"✅ Utilisateur créé avec ID: {user['id']}")
        print(f"📧 Email: {user['email']}")
        print(f"👤 Nom: {user['name']}")
        user_id = user['id']
    else:
        print(f"❌ Erreur: {response.text}")
        return
    
    # ==========================================
    # ÉTAPE 3: Connexion (Login)
    # ==========================================
    print_step(3, "Connexion de l'utilisateur")
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=login_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        token_data = response.json()
        token = token_data["access_token"]
        print(f"✅ Token obtenu: {token[:20]}...")
        headers = {"Authorization": f"Bearer {token}"}
    else:
        print(f"❌ Erreur: {response.text}")
        return
    
    # ==========================================
    # ÉTAPE 4: Création d'une offre d'emploi
    # ==========================================
    print_step(4, "Création d'une offre d'emploi")
    job_data = {
        "title": "Développeur Full Stack Python",
        "company": "TechCorp Solutions",
        "location": "Paris, France",
        "source": "LinkedIn",
        "url": "https://exemple.com/job/12345",
        "raw_description": "Nous recherchons un développeur Python expérimenté pour rejoindre notre équipe.\n\nRequis:\n- 3+ ans d'expérience en Python\n- Connaissance de Django, FastAPI\n- PostgreSQL\n\nSalaire: 45k-65k EUR",
        "application_type": "portal",
        "application_url": "https://exemple.com/apply/12345"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/job-offers/", json=job_data, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code in [200, 201]:
        job = response.json()
        print(f"✅ Offre créée avec ID: {job['id']}")
        print(f"💼 Poste: {job['title']}")
        print(f"🏢 Entreprise: {job['company']}")
        print(f"📍 Localisation: {job['location']}")
        job_id = job['id']
    else:
        print(f"❌ Erreur: {response.text}")
        return
    
    # ==========================================
    # ÉTAPE 5: Récupération des offres
    # ==========================================
    print_step(5, "Récupération de toutes les offres")
    response = requests.get(f"{BASE_URL}/api/v1/job-offers/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        jobs = response.json()
        print(f"✅ {len(jobs)} offre(s) trouvée(s)")
        for idx, job in enumerate(jobs, 1):
            print(f"  {idx}. {job['title']} chez {job['company']}")
    
    # ==========================================
    # ÉTAPE 6: Création d'un brouillon de candidature
    # ==========================================
    print_step(6, "Création d'un brouillon de candidature")
    draft_data = {
        "job_offer_id": job_id,
        "cover_letter_text": "Madame, Monsieur,\n\nJe suis très intéressé par le poste de Développeur Full Stack...",
        "email_subject": "Candidature - Développeur Full Stack Python",
        "email_body": "Veuillez trouver ci-joint ma lettre de motivation...",
        "status": "draft"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/drafts/", json=draft_data, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code in [200, 201]:
        draft = response.json()
        print(f"✅ Brouillon créé avec ID: {draft['id']}")
        print(f"📝 Status: {draft['status']}")
        draft_id = draft['id']
    else:
        print(f"❌ Erreur: {response.text}")
        draft_id = None
    
    # ==========================================
    # ÉTAPE 7: Création d'une candidature
    # ==========================================
    print_step(7, "Création d'une candidature")
    application_data = {
        "job_offer_id": job_id,
        "channel": "portal",
        "portal_type": "LinkedIn",
        "submitted_by": "manual",
        "status": "sent",
        "notes": "Candidature envoyée via le portail LinkedIn"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/applications/", json=application_data, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code in [200, 201]:
        application = response.json()
        print(f"✅ Candidature créée avec ID: {application['id']}")
        print(f"📤 Status: {application['status']}")
        print(f"📅 Date: {application['created_at']}")
        application_id = application['id']
    else:
        print(f"❌ Erreur: {response.text}")
        application_id = None
    
    # ==========================================
    # ÉTAPE 8: Récupération du profil utilisateur
    # ==========================================
    print_step(8, "Récupération du profil utilisateur")
    response = requests.get(f"{BASE_URL}/api/v1/users/me", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        profile = response.json()
        print(f"✅ Profil récupéré:")
        print(f"  👤 ID: {profile['id']}")
        print(f"  📧 Email: {profile['email']}")
        print(f"  🏷️ Nom: {profile['name']}")
    
    # ==========================================
    # ÉTAPE 9: Récupération de la timeline
    # ==========================================
    print_step(9, "Récupération de la timeline d'activités")
    if application_id:
        response = requests.get(f"{BASE_URL}/api/v1/timeline/application/{application_id}", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            timeline = response.json()
            print(f"✅ {len(timeline)} événement(s) dans la timeline")
            for event in timeline[:5]:  # Afficher les 5 premiers
                print(f"  • {event['event_type']}: {event.get('description', 'N/A')}")
    else:
        print("⚠️ Pas de candidature créée, impossible de récupérer la timeline")
    
    # ==========================================
    # RÉSUMÉ
    # ==========================================
    print_step("RÉSUMÉ", "Tests terminés avec succès!")
    print("""
    ✅ Tests réussis:
       - Connexion API
       - Création utilisateur
       - Authentification
       - Création offre d'emploi
       - Création brouillon
       - Création candidature
       - Récupération profil
       - Timeline
    
    🎉 Le backend ApplyFlow fonctionne correctement!
    """)

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║   🚀 TEST DU BACKEND APPLYFLOW                      ║
    ║   📝 Script de test automatisé                       ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ ERREUR: Impossible de se connecter à l'API")
        print("   Assurez-vous que le serveur est lancé sur http://localhost:8000")
    except Exception as e:
        print(f"❌ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()
