# 📘 Guide d'Intégration Frontend - ApplyFlow Backend

**Date :** 5 décembre 2025  
**Version Backend :** Multi-User Ready  
**Migrations :** `14143f09b0ab` + `2031f3d10fe2`

---

## 🎯 Résumé pour le Frontend

Le backend ApplyFlow est maintenant **100% compatible multi-utilisateur** avec isolation complète des données. Chaque utilisateur dispose de son propre espace isolé (offres, candidatures, drafts, etc.).

### ✨ Nouvelles Fonctionnalités

1. **Isolation Multi-User** : Tous les endpoints filtrent automatiquement par `user_id`
2. **Validation CV** : Erreurs 400 explicites si le CV n'est pas uploadé
3. **Endpoint Send Draft** : `POST /drafts/{draft_id}/send` pour créer une application

---

## 🔐 Authentification

### Login
```http
POST /api/v1/auth/login
Content-Type: multipart/form-data

username=user@example.com
password=securepass123
```

**Réponse 200 :**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Utiliser le Token
Inclure dans **tous** les headers de requête :
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Register
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepass123",
  "name": "John Doe"
}
```

**Réponse 200 :**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2025-12-05T14:30:00Z"
}
```

---

## 📋 Endpoints Principaux

### 1. Profil Utilisateur

#### GET /users/me
Récupère le profil de l'utilisateur connecté.

```http
GET /api/v1/users/me
Authorization: Bearer {token}
```

**Réponse 200 :**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "cv_file_path": "/uploads/cv_user1.pdf",
  "cv_text": "Extracted text from CV...",
  "cover_letter_template": "Dear Hiring Manager,\n\n[BODY]\n\nSincerely,\n[NAME]",
  "linkedin_url": "https://linkedin.com/in/johndoe",
  "profile_summary": "Senior developer with 5 years experience...",
  "created_at": "2025-12-05T14:30:00Z",
  "updated_at": "2025-12-05T14:30:00Z"
}
```

#### POST /users/upload-cv
Upload du CV (requis avant analyse).

```http
POST /api/v1/users/upload-cv
Authorization: Bearer {token}
Content-Type: multipart/form-data

file=@cv.pdf
```

**Réponse 200 :**
```json
{
  "message": "CV uploaded successfully",
  "cv_path": "/uploads/cv_user1.pdf"
}
```

#### PUT /users/me
Mettre à jour le profil.

```http
PUT /api/v1/users/me
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "John Doe Updated",
  "linkedin_url": "https://linkedin.com/in/johndoe",
  "profile_summary": "Updated summary...",
  "cover_letter_template": "Custom template..."
}
```

---

### 2. Offres d'Emploi

#### ✨ POST /job-offers/scrape (NOUVEAU)
Scrape les détails d'une offre depuis une URL.

```http
POST /api/v1/job-offers/scrape
Authorization: Bearer {token}
Content-Type: application/json

{
  "url": "https://www.linkedin.com/jobs/view/12345/"
}
```

**Réponse 200 :**
```json
{
  "title": "Senior Python Developer",
  "company": "TechCorp",
  "location": "Paris, France",
  "description": "We are looking for a passionate developer...",
  "application_type": "portal",
  "application_url": "https://www.linkedin.com/jobs/view/12345/"
}
```

**⚠️ Erreur 400 (plateforme non supportée) :**
```json
{
  "detail": "Platform not supported. Supported platforms: LinkedIn, Indeed, Welcome to the Jungle."
}
```

**Plateformes supportées :**
- ✅ LinkedIn (linkedin.com)
- ✅ Indeed (indeed.com, indeed.fr)
- ✅ Welcome to the Jungle (welcometothejungle.com, wttj.co)

**Utilisation dans le workflow :**
```javascript
// 1. Scraper l'offre
const scraped = await fetch('/api/v1/job-offers/scrape', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    url: 'https://www.linkedin.com/jobs/view/12345/'
  })
}).then(r => r.json());

// 2. Créer l'offre avec les données scrapées
const jobOffer = await fetch('/api/v1/job-offers/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    title: scraped.title,
    company: scraped.company,
    source: 'LinkedIn',  // Détecté depuis l'URL
    url: scraped.application_url,
    application_type: scraped.application_type,
    application_url: scraped.application_url,
    raw_description: scraped.description,
    location: scraped.location
  })
}).then(r => r.json());
```

#### GET /job-offers/
Liste des offres de l'utilisateur connecté **uniquement**.

```http
GET /api/v1/job-offers/?skip=0&limit=50
Authorization: Bearer {token}
```

**Réponse 200 :**
```json
[
  {
    "id": 1,
    "title": "Senior Python Developer",
    "company": "TechCorp",
    "source": "LinkedIn",
    "url": "https://techcorp.com/jobs/python",
    "application_type": "portal",
    "application_url": "https://www.linkedin.com/jobs/view/12345/",
    "raw_description": "We are looking for...",
    "location": "Paris, France",
    "user_id": 1,
    "created_at": "2025-12-05T10:00:00Z"
  }
]
```

**⚠️ Important :** Retourne **SEULEMENT** les offres créées par l'utilisateur connecté.

**Champs JobOffer :**
- `source` ✅ "LinkedIn", "Indeed", "Manual", etc.
- `application_type` ✅ "email", "portal", "linkedin_easy_apply", "manual"
- `application_url` ✅ URL de candidature ou email
- `raw_description` ✅ Description brute (pas `description`)

#### POST /job-offers/
Créer une nouvelle offre.

```http
POST /api/v1/job-offers/
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Senior Python Developer",
  "company": "TechCorp",
  "source": "LinkedIn",
  "url": "https://techcorp.com/jobs/python",
  "application_type": "portal",
  "application_url": "https://www.linkedin.com/jobs/view/12345/",
  "raw_description": "We are looking for...",
  "location": "Paris, France"
}
```

**Champs requis :**
- `title` (string)
- `company` (string)
- `source` (string)
- `raw_description` (text)

**Champs optionnels :**
- `location` (string)
- `url` (string)
- `application_type` (string, default: "email")
- `application_url` (string)

#### GET /job-offers/{id}
Détails d'une offre (doit appartenir à l'utilisateur).

```http
GET /api/v1/job-offers/1
Authorization: Bearer {token}
```

**Erreur 404 :** Si l'offre appartient à un autre utilisateur.

---

### 3. Analyse de Match (Job Matches)

#### POST /job-matches/analyze/{job_offer_id}
Analyser le match entre le CV et l'offre.

```http
POST /api/v1/job-matches/analyze/1
Authorization: Bearer {token}
```

**Réponse 200 (si CV uploadé) :**
```json
{
  "id": 1,
  "job_offer_id": 1,
  "match_score": 85,
  "strengths": ["Python", "FastAPI", "PostgreSQL"],
  "weaknesses": ["Kubernetes"],
  "recommendations": "Consider highlighting your Python experience...",
  "user_id": 1,
  "created_at": "2025-12-05T10:15:00Z"
}
```

**⚠️ Erreur 400 (si CV manquant) :**
```json
{
  "detail": "You must upload your CV first. Please go to your profile to upload your CV."
}
```

**Détection Frontend :**
```javascript
if (error.status === 400 && 
    error.detail.includes('upload') && 
    error.detail.includes('CV')) {
  // Afficher message : "Veuillez d'abord uploader votre CV"
  // Rediriger vers /profile
}
```

#### GET /job-matches/{job_offer_id}
Récupérer l'analyse existante.

```http
GET /api/v1/job-matches/1
Authorization: Bearer {token}
```

---

### 4. Drafts (Brouillons de Candidature)

#### POST /drafts/generate/{job_offer_id}
Générer un draft automatiquement avec l'IA.

```http
POST /api/v1/drafts/generate/1
Authorization: Bearer {token}
```

**⚠️ Erreur 400 (si CV manquant) :**
```json
{
  "detail": "You must upload your CV first. Please go to your profile to upload your CV."
}
```

**Réponse 200 :**
```json
{
  "id": 1,
  "job_offer_id": 1,
  "cover_letter_text": "Dear Hiring Manager...",
  "email_subject": "Application for Senior Python Developer",
  "email_body": "Dear Hiring Manager,\n\nI am writing to...",
  "status": "draft",
  "user_id": 1,
  "created_at": "2025-12-05T10:20:00Z"
}
```

**Champs ApplicationDraft :**
- `cover_letter_text` ✅ (pas `cover_letter_content`)
- `email_subject` ✅
- `email_body` ✅
- `cover_letter_pdf_path` ✅
- `attachments` ✅ (JSON string)
- `status` ✅ "draft" ou "ready"

#### GET /drafts/
Liste tous les drafts de l'utilisateur.

```http
GET /api/v1/drafts/?skip=0&limit=50
Authorization: Bearer {token}
```

#### GET /drafts/{job_offer_id}
Récupérer le draft pour une offre spécifique.

```http
GET /api/v1/drafts/1
Authorization: Bearer {token}
```

#### PUT /drafts/{draft_id}
Modifier un draft existant.

```http
PUT /api/v1/drafts/1
Authorization: Bearer {token}
Content-Type: application/json

{
  "cover_letter_text": "Updated cover letter...",
  "email_subject": "Updated subject",
  "email_body": "Updated email body...",
  "status": "draft"
}
```

**Tous les champs sont optionnels dans le PUT.**

#### ✨ POST /drafts/{draft_id}/send
**NOUVEAU** - Marquer le draft comme envoyé et créer une application.

```http
POST /api/v1/drafts/1/send
Authorization: Bearer {token}
```

**Réponse 200 :**
```json
{
  "success": true,
  "message": "Draft marked as sent and application created successfully.",
  "application_id": 5,
  "draft_id": 1
}
```

**Comportement :**
1. Vérifie que le draft appartient à l'utilisateur connecté
2. Crée une nouvelle `Application` avec `status="sent"`
3. Met à jour le draft : `status="sent"`
4. Si une application existe déjà pour cette offre, retourne l'existante

**Erreur 404 :** Si le draft n'existe pas ou appartient à un autre utilisateur.

#### DELETE /drafts/{draft_id}
Supprimer un draft.

```http
DELETE /api/v1/drafts/1
Authorization: Bearer {token}
```

---

### 5. Applications (Candidatures Envoyées)

#### GET /applications/
Liste toutes les applications de l'utilisateur.

```http
GET /api/v1/applications/?skip=0&limit=50
Authorization: Bearer {token}
```

**Réponse 200 :**
```json
[
  {
    "id": 1,
    "job_offer_id": 1,
    "status": "sent",
    "applied_at": "2025-12-05T11:00:00Z",
    "cover_letter_content": "Dear Hiring Manager...",
    "user_id": 1,
    "job_offer": {
      "title": "Senior Python Developer",
      "company": "TechCorp"
    }
  }
]
```

**⚠️ Important :** Retourne **SEULEMENT** les applications de l'utilisateur connecté.

#### GET /applications/{id}
Détails d'une application.

```http
GET /api/v1/applications/1
Authorization: Bearer {token}
```

#### PUT /applications/{id}
Mettre à jour le status d'une application.

```http
PUT /api/v1/applications/1
Authorization: Bearer {token}
Content-Type: application/json

{
  "status": "interview_scheduled",
  "notes": "Phone interview scheduled for Monday 10am"
}
```

**Status possibles :**
- `sent` - Envoyée
- `viewed` - Vue par le recruteur
- `interview_scheduled` - Entretien programmé
- `rejected` - Refusée
- `accepted` - Acceptée

---

### 6. Timeline (Historique)

#### GET /timeline/events/
Historique des événements de l'utilisateur.

```http
GET /api/v1/timeline/events/?skip=0&limit=50
Authorization: Bearer {token}
```

**Réponse 200 :**
```json
[
  {
    "id": 1,
    "event_type": "application_sent",
    "description": "Applied to Senior Python Developer at TechCorp",
    "job_offer_id": 1,
    "application_id": 1,
    "user_id": 1,
    "created_at": "2025-12-05T11:00:00Z"
  }
]
```

**Types d'événements :**
- `job_offer_created`
- `match_analyzed`
- `draft_generated`
- `application_sent`
- `status_updated`

---

## 🔄 Workflow Complet

### Scénario : Postuler à une offre

```javascript
// 1. Vérifier que l'utilisateur a un CV
const user = await fetch('/api/v1/users/me', {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json());

if (!user.cv_file_path) {
  // Rediriger vers /profile pour upload CV
  router.push('/profile');
  return;
}

// 2. Créer une offre d'emploi
const jobOffer = await fetch('/api/v1/job-offers/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    title: 'Senior Python Developer',
    company: 'TechCorp',
    url: 'https://techcorp.com/jobs/python',
    description: '...',
    location: 'Paris',
    salary: '60000-80000',
    contract_type: 'CDI'
  })
}).then(r => r.json());

const jobOfferId = jobOffer.id;

// 3. Analyser le match
try {
  const match = await fetch(`/api/v1/job-matches/analyze/${jobOfferId}`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  }).then(r => r.json());
  
  console.log('Match score:', match.match_score);
  
} catch (error) {
  if (error.status === 400 && error.detail.includes('CV')) {
    // Afficher : "Veuillez uploader votre CV"
  }
}

// 4. Générer un draft
const draft = await fetch(`/api/v1/drafts/generate/${jobOfferId}`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json());

console.log('Draft generated:', draft.id);

// 5. (Optionnel) Modifier le draft
await fetch(`/api/v1/drafts/${draft.id}`, {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    cover_letter_content: 'Updated content...'
  })
});

// 6. Envoyer la candidature
const result = await fetch(`/api/v1/drafts/${draft.id}/send`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json());

console.log('Application sent:', result.application_id);

// 7. Voir la candidature dans la liste
const applications = await fetch('/api/v1/applications/', {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json());

console.log('My applications:', applications);
```

---

## 🚨 Gestion des Erreurs

### Erreurs Courantes

#### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```
**Action :** Token invalide/expiré → Déconnecter l'utilisateur et rediriger vers `/login`

#### 400 CV Manquant
```json
{
  "detail": "You must upload your CV first. Please go to your profile to upload your CV."
}
```
**Action :** Afficher message + rediriger vers `/profile`

**Détection :**
```javascript
if (error.status === 400 && 
    error.detail.toLowerCase().includes('upload') && 
    error.detail.toLowerCase().includes('cv')) {
  showNotification('Veuillez d\'abord uploader votre CV', 'warning');
  router.push('/profile');
}
```

#### 404 Not Found
```json
{
  "detail": "Job offer not found"
}
```
**Raisons possibles :**
1. L'ID n'existe pas
2. La ressource appartient à un autre utilisateur (isolation)

**Action :** Afficher "Ressource introuvable" + retour à la liste

#### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```
**Action :** Afficher les erreurs de validation sur les champs concernés

---

## 🔒 Sécurité & Isolation

### Principes

1. **Isolation Automatique** : Tous les endpoints filtrent par `user_id` du token JWT
2. **Pas d'accès croisé** : Un utilisateur ne peut PAS voir/modifier les données d'un autre
3. **Validation Ownership** : Chaque opération vérifie que la ressource appartient à l'utilisateur

### Exemple d'Isolation

```javascript
// User 1 crée une offre
const user1Token = 'token_user1';
const offer = await createJobOffer(user1Token, { title: 'Dev Python' });
// offer.id = 1, offer.user_id = 1

// User 2 essaie d'accéder à l'offre de User 1
const user2Token = 'token_user2';
const result = await fetch('/api/v1/job-offers/1', {
  headers: { 'Authorization': `Bearer ${user2Token}` }
});
// Résultat : 404 Not Found (comme si l'offre n'existait pas)

// User 2 voit sa propre liste (vide)
const offers = await fetch('/api/v1/job-offers/', {
  headers: { 'Authorization': `Bearer ${user2Token}` }
}).then(r => r.json());
// Résultat : []
```

### Bonnes Pratiques Frontend

✅ **Faire :**
- Stocker le token de manière sécurisée (httpOnly cookie ou localStorage avec précautions)
- Vérifier le status HTTP et gérer les erreurs 401/403/404
- Afficher des messages clairs pour les erreurs 400 CV manquant
- Rafraîchir le token avant expiration

❌ **Ne PAS faire :**
- Cacher les IDs dans l'URL (l'isolation backend suffit)
- Assumer qu'un ID existe sans vérifier la réponse 404
- Ignorer les erreurs de validation

---

## 📊 Modèles de Données

### User
```typescript
interface User {
  id: number;
  email: string;
  name: string;
  cv_file_path?: string;
  cv_text?: string;
  cover_letter_template?: string;   // ✅ Existe
  linkedin_url?: string;
  profile_summary?: string;
  created_at: string;
  updated_at: string;
}
```

### JobOffer
```typescript
interface JobOffer {
  id: number;
  title: string;
  company: string;
  source: string;                   // "LinkedIn", "Indeed", "Manual", etc.
  url?: string;
  application_type: string;         // "email", "portal", "linkedin_easy_apply", "manual"
  application_url?: string;         // URL de candidature ou email
  raw_description: string;          // ⚠️ Pas "description"
  location?: string;
  user_id: number;
  created_at: string;
  updated_at: string;
}
```

### JobMatch
```typescript
interface JobMatch {
  id: number;
  job_offer_id: number;
  match_score: number;
  strengths: string[];
  weaknesses: string[];
  recommendations?: string;
  user_id: number;
  created_at: string;
}
```

### ApplicationDraft
```typescript
interface ApplicationDraft {
  id: number;
  job_offer_id: number;
  cover_letter_text: string;        // ⚠️ Pas cover_letter_content
  cover_letter_pdf_path?: string;
  email_subject?: string;
  email_body?: string;
  attachments?: string;             // JSON string
  status: 'draft' | 'ready';
  user_id: number;
  created_at: string;
  updated_at: string;
}
```

### Application
```typescript
interface Application {
  id: number;
  job_offer_id: number;
  status: 'sent' | 'viewed' | 'interview_scheduled' | 'rejected' | 'accepted';
  applied_at: string;
  cover_letter_content: string;
  notes?: string;
  user_id: number;
  job_offer?: JobOffer; // Populated with join
}
```

### TimelineEvent
```typescript
interface TimelineEvent {
  id: number;
  event_type: string;
  description: string;
  job_offer_id?: number;
  application_id?: number;
  user_id: number;
  created_at: string;
}
```

---

## 🧪 Tests avec cURL

### Créer un utilisateur et tester le workflow

```bash
# 1. Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "name": "Test User"
  }'

# 2. Login
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -F "username=test@example.com" \
  -F "password=testpass123" \
  | jq -r '.access_token')

# 3. Upload CV
curl -X POST http://localhost:8000/api/v1/users/upload-cv \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@cv.pdf"

# 4. Créer une offre
JOB_ID=$(curl -X POST http://localhost:8000/api/v1/job-offers/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Developer",
    "company": "TechCorp",
    "url": "https://example.com/job"
  }' | jq -r '.id')

# 5. Analyser le match
curl -X POST http://localhost:8000/api/v1/job-matches/analyze/$JOB_ID \
  -H "Authorization: Bearer $TOKEN" | jq

# 6. Générer draft
DRAFT_ID=$(curl -X POST http://localhost:8000/api/v1/drafts/generate/$JOB_ID \
  -H "Authorization: Bearer $TOKEN" | jq -r '.id')

# 7. Envoyer la candidature
curl -X POST http://localhost:8000/api/v1/drafts/$DRAFT_ID/send \
  -H "Authorization: Bearer $TOKEN" | jq

# 8. Voir les applications
curl -X GET http://localhost:8000/api/v1/applications/ \
  -H "Authorization: Bearer $TOKEN" | jq
```

---

## 🔧 Configuration

### Base URL
```javascript
const API_BASE_URL = 'http://localhost:8000/api/v1';
```

En production :
```javascript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.applyflow.com/v1';
```

### Headers par Défaut
```javascript
const defaultHeaders = {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${getToken()}`
};
```

---

## 📝 Notes Importantes

### CV Requis
Les endpoints suivants **nécessitent** un CV uploadé :
- `POST /job-matches/analyze/{id}`
- `POST /drafts/generate/{id}`
- `POST /drafts/{id}` (create)

**Toujours vérifier** que `user.cv_file_path` existe avant d'appeler ces endpoints.

### Pagination
Les endpoints de liste acceptent `skip` et `limit` :
```http
GET /api/v1/job-offers/?skip=0&limit=20
```

Par défaut : `skip=0`, `limit=100`

### Timestamps
Tous les timestamps sont en **UTC** au format ISO 8601 :
```
2025-12-05T14:30:00Z
```

### IDs
Tous les IDs sont des **entiers** (integer).

---

## 🐛 Debug

### Activer les logs détaillés
Le backend log toutes les requêtes en mode DEBUG.

Chercher dans les logs :
```
[info] http_request client=(...) method=POST path=/api/v1/drafts/1/send
[error] database_error error=(...)
```

### Swagger UI
Documentation interactive disponible sur :
```
http://localhost:8000/docs
```

Permet de tester tous les endpoints directement dans le navigateur.

---

## ✅ Checklist Intégration

- [ ] Configuration de l'URL backend
- [ ] Système d'authentification (login/register)
- [ ] Stockage sécurisé du token JWT
- [ ] Gestion erreur 401 → redirection login
- [ ] Gestion erreur 400 CV manquant → redirection profile
- [ ] Upload CV dans le profil utilisateur
- [ ] Liste des offres d'emploi avec isolation
- [ ] Analyse de match avec validation CV
- [ ] Génération de draft avec validation CV
- [ ] Modification de draft
- [ ] Envoi de candidature (POST /send)
- [ ] Liste des applications envoyées
- [ ] Timeline des événements
- [ ] Tests avec 2 utilisateurs différents

---

## 🚀 Support

- **Documentation complète :** `SUMMARY_MIGRATION.md`
- **Quick Start :** `QUICKSTART_MULTI_USER.md`
- **Vérification :** `VERIFICATION_FRONTEND.md`
- **API Interactive :** http://localhost:8000/docs

---

**Version :** 1.0.0 Multi-User  
**Dernière mise à jour :** 5 décembre 2025
