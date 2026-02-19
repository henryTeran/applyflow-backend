# 🚀 Guide de Démarrage Rapide - ApplyFlow Multi-User

## Démarrage du Backend

### 1. Vérifier les migrations
```bash
cd /mnt/c/projets/ApplyFlow/backend

# Vérifier la version actuelle
alembic current

# Doit afficher : 2031f3d10fe2 (head)
```

### 2. Lancer le serveur
```bash
# Activer l'environnement conda (si utilisé)
conda activate applyflow

# Démarrer le serveur
uvicorn app.main:app --reload --port 8000

# Ou utiliser le script start
./start.sh  # Linux/WSL
# OU
start.bat   # Windows
```

### 3. Vérifier que tout fonctionne
```bash
# Dans un nouveau terminal
python check_frontend_requirements.py

# Doit afficher :
# ✅ PASS - send_draft
# ✅ PASS - filter_job_offers
# ✅ PASS - filter_applications
# ✅ PASS - cv_check_analyze
# ✅ PASS - cv_check_generate
# 🎉 TOUS LES POINTS FRONTEND SONT CONFORMES !
```

---

## Tester le Multi-User

### Étape 1 : Créer 2 utilisateurs

```bash
# User 1
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "securepass123",
    "name": "Alice Developer"
  }'

# User 2
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "bob@example.com",
    "password": "securepass456",
    "name": "Bob Engineer"
  }'
```

### Étape 2 : Se connecter

```bash
# Login Alice
TOKEN_ALICE=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -F "username=alice@example.com" \
  -F "password=securepass123" \
  | jq -r '.access_token')

echo "Token Alice: $TOKEN_ALICE"

# Login Bob
TOKEN_BOB=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -F "username=bob@example.com" \
  -F "password=securepass456" \
  | jq -r '.access_token')

echo "Token Bob: $TOKEN_BOB"
```

### Étape 3 : Alice crée une offre

```bash
curl -X POST http://localhost:8000/api/v1/job-offers/ \
  -H "Authorization: Bearer $TOKEN_ALICE" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Python Developer",
    "company": "TechCorp",
    "url": "https://techcorp.com/jobs/python-dev",
    "description": "We are looking for a senior Python developer...",
    "location": "Paris, France",
    "salary": "60000-80000",
    "contract_type": "CDI"
  }'
```

### Étape 4 : Vérifier l'isolation

```bash
# Alice voit ses offres
curl -X GET http://localhost:8000/api/v1/job-offers/ \
  -H "Authorization: Bearer $TOKEN_ALICE" | jq

# Doit retourner 1 offre

# Bob ne voit PAS les offres d'Alice
curl -X GET http://localhost:8000/api/v1/job-offers/ \
  -H "Authorization: Bearer $TOKEN_BOB" | jq

# Doit retourner []
```

### Étape 5 : Tester la validation CV

```bash
# Essayer d'analyser sans CV (doit échouer avec 400)
curl -X POST http://localhost:8000/api/v1/job-matches/analyze/1 \
  -H "Authorization: Bearer $TOKEN_ALICE" | jq

# Réponse attendue :
# {
#   "detail": "You must upload your CV first. Please go to your profile to upload your CV."
# }

# Upload du CV
curl -X POST http://localhost:8000/api/v1/users/upload-cv \
  -H "Authorization: Bearer $TOKEN_ALICE" \
  -F "file=@/path/to/your/cv.pdf"

# Maintenant l'analyse devrait fonctionner
curl -X POST http://localhost:8000/api/v1/job-matches/analyze/1 \
  -H "Authorization: Bearer $TOKEN_ALICE" | jq
```

### Étape 6 : Tester le workflow complet

```bash
# 1. Alice crée une offre (déjà fait ci-dessus)
JOB_ID=1

# 2. Lancer l'analyse de match
curl -X POST http://localhost:8000/api/v1/job-matches/analyze/$JOB_ID \
  -H "Authorization: Bearer $TOKEN_ALICE" | jq

# 3. Générer un draft
curl -X POST http://localhost:8000/api/v1/drafts/generate/$JOB_ID \
  -H "Authorization: Bearer $TOKEN_ALICE" | jq

# 4. Récupérer le draft
DRAFT_ID=1
curl -X GET http://localhost:8000/api/v1/drafts/$DRAFT_ID \
  -H "Authorization: Bearer $TOKEN_ALICE" | jq

# 5. Modifier le draft si nécessaire
curl -X PUT http://localhost:8000/api/v1/drafts/$DRAFT_ID \
  -H "Authorization: Bearer $TOKEN_ALICE" \
  -H "Content-Type: application/json" \
  -d '{
    "cover_letter_content": "Updated cover letter..."
  }' | jq

# 6. Marquer le draft comme envoyé (créer application)
curl -X POST http://localhost:8000/api/v1/drafts/$DRAFT_ID/send \
  -H "Authorization: Bearer $TOKEN_ALICE" | jq

# Réponse attendue :
# {
#   "success": true,
#   "message": "Draft marked as sent and application created successfully.",
#   "application_id": 1,
#   "draft_id": 1
# }

# 7. Vérifier l'application créée
curl -X GET http://localhost:8000/api/v1/applications/ \
  -H "Authorization: Bearer $TOKEN_ALICE" | jq
```

---

## Tester avec le Frontend

### Configuration
Le frontend doit pointer vers `http://localhost:8000/api/v1`

### Points Clés

1. **Authentification** : Utiliser le token JWT dans le header `Authorization: Bearer {token}`

2. **Erreurs CV** : Détecter les erreurs 400 contenant "upload" et "CV" pour afficher un message

3. **Isolation** : Chaque utilisateur ne voit que ses propres données

4. **Workflow Draft→Application** :
   ```
   GET /job-offers/           → Liste offres
   POST /job-matches/analyze/  → Analyser match
   POST /drafts/generate/      → Générer draft
   GET /drafts/{id}            → Consulter draft
   PUT /drafts/{id}            → Modifier draft
   POST /drafts/{id}/send      → Convertir en application
   GET /applications/          → Liste applications envoyées
   ```

---

## Débogage

### Vérifier les logs
```bash
# Les logs s'affichent dans le terminal où uvicorn tourne
# Rechercher :
# - [error] pour les erreurs
# - [info] pour les requêtes HTTP
# - [debug] pour les détails

# Exemple log réussi :
# [info] http_request client=('127.0.0.1', 56789) method=POST path=/api/v1/drafts/1/send
```

### Vérifier la base de données
```bash
# Connexion PostgreSQL
PGPASSWORD=postgres psql -h localhost -U postgres -d applyflow

# Vérifier les users
SELECT id, email, name, cv_file_path FROM users;

# Vérifier les offres par user
SELECT id, title, user_id FROM job_offers;

# Vérifier les applications
SELECT id, job_offer_id, user_id, status FROM applications;

# Quitter
\q
```

### Réinitialiser la base (ATTENTION : efface tout)
```bash
# Supprimer toutes les données
PGPASSWORD=postgres psql -h localhost -U postgres -d applyflow -c "TRUNCATE users CASCADE;"

# Réappliquer les migrations
alembic downgrade base
alembic upgrade head
```

---

## Erreurs Courantes

### 1. "column users.cv_file_path does not exist"
**Solution :** Migration non appliquée
```bash
alembic upgrade head
```

### 2. "401 Unauthorized"
**Solution :** Token expiré ou invalide
```bash
# Se reconnecter pour obtenir un nouveau token
```

### 3. "404 Not Found" sur un ID
**Solution :** L'objet appartient à un autre user
```bash
# Vérifier l'ownership dans les logs
```

### 4. "400 You must upload your CV first"
**Solution :** Upload du CV nécessaire
```bash
curl -X POST http://localhost:8000/api/v1/users/upload-cv \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@cv.pdf"
```

---

## Support

- **Documentation :** `VERIFICATION_FRONTEND.md`
- **Résumé Migration :** `SUMMARY_MIGRATION.md`
- **Tests Auto :** `python check_frontend_requirements.py`
- **API Swagger :** http://localhost:8000/docs

---

*Bonne chance avec l'intégration ! 🚀*
