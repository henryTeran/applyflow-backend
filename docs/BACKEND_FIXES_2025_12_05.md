# 🔧 Backend Fixes - 5 décembre 2025

## ✅ Corrections Implémentées

### 1. **Fix /users/me - Retourne maintenant l'utilisateur authentifié**

**Problème:** L'endpoint `/api/v1/users/me` retournait le premier utilisateur de la base au lieu de l'utilisateur connecté via JWT.

**Solution:**
- Supprimé le stub `get_current_user()` de `app/api/deps.py`
- Utilisé la vraie implémentation JWT de `app/api/v1/auth.py`
- L'endpoint utilise maintenant `Depends(get_current_user)` pour identifier l'utilisateur via le token

**Code avant:**
```python
@router.get("/me", response_model=UserRead)
def get_current_user_info(db: Session = Depends(get_db)):
    users = crud.list_users(db, limit=1)
    return users[0]  # ❌ Retourne toujours le premier user
```

**Code après:**
```python
@router.get("/me", response_model=UserRead)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user  # ✅ Retourne l'user du token JWT
```

---

### 2. **Ajout des champs CV et template au modèle User**

**Nouveaux champs ajoutés:**
- `cv_path: Optional[str]` - Chemin vers le fichier CV (PDF)
- `cover_letter_template: Optional[str]` - Template personnalisé pour les lettres de motivation

**Fichiers modifiés:**
- `app/models/user.py` - Colonnes SQLAlchemy
- `app/schemas/user.py` - Schemas Pydantic (UserRead, UserUpdate)

**Migration Alembic:**
```bash
alembic revision -m "add_cv_path_and_template_to_users"
alembic upgrade head
```

**Fichier:** `alembic/versions/bf4f2a4a904c_add_cv_path_and_template_to_users.py`

**Vérification base de données:**
```sql
-- Table users maintenant avec:
cv_path                        VARCHAR(500)         NULL
cover_letter_template          TEXT                 NULL
```

---

### 3. **Filtrage par user_id pour les job offers**

**Nouveau paramètre ajouté:**
```python
@router.get("/", response_model=List[JobOfferRead])
def list_job_offers(
    user_id: Optional[int] = None,  # ✨ Nouveau
    # ... autres params
):
```

**Usage:**
```bash
# Toutes les offres
GET /api/v1/job-offers/

# Offres d'un utilisateur spécifique
GET /api/v1/job-offers/?user_id=1
```

**Fichiers modifiés:**
- `app/api/v1/job_offers.py` - Endpoint avec paramètre
- `app/crud/job_offer.py` - Logique de filtrage

---

### 4. **Endpoint POST /users/upload-cv**

**Nouveau endpoint pour uploader le CV:**

```python
@router.post("/upload-cv")
async def upload_cv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload user CV (PDF only)."""
```

**Fonctionnalités:**
- ✅ Validation: Accepte uniquement les PDF
- ✅ Stockage: `uploads/cv/{user_id}_{filename}.pdf`
- ✅ Update automatique de `user.cv_path` en DB
- ✅ Authentification JWT requise

**Usage frontend:**
```typescript
const formData = new FormData();
formData.append('file', cvFile);

await fetch('/api/v1/users/upload-cv', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});
```

---

### 5. **Endpoint PATCH /users/me**

**Nouveau endpoint pour mettre à jour son propre profil:**

```python
@router.patch("/me", response_model=UserRead)
def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
```

**Champs modifiables:**
- `name`
- `email`
- `password`
- `cv_path`
- `cover_letter_template`

**Usage:**
```bash
PATCH /api/v1/users/me
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Nouveau nom",
  "cover_letter_template": "Mon template personnalisé..."
}
```

---

## 📊 Résumé des Changements

| Fichier | Changements |
|---------|-------------|
| `app/api/deps.py` | ❌ Supprimé stub `get_current_user()` |
| `app/api/v1/auth.py` | ✅ get_current_user() déjà implémenté avec JWT |
| `app/api/v1/users.py` | ✅ Fix /me, Ajout PATCH /me, Ajout POST /upload-cv |
| `app/api/v1/job_offers.py` | ✅ Ajout filtrage user_id |
| `app/models/user.py` | ✅ Colonnes cv_path + cover_letter_template |
| `app/schemas/user.py` | ✅ Schémas UserRead/Update mis à jour |
| `app/crud/job_offer.py` | ✅ Fonction list_job_offers() avec user_id |
| `alembic/versions/bf4f2a4a904c_*.py` | ✅ Migration pour nouvelles colonnes |

---

## 🧪 Tests Recommandés

### Test 1: Authentification et /users/me
```bash
# 1. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123"}'

# Réponse: {"access_token":"eyJ...", "token_type":"bearer"}

# 2. Get /me avec token
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer eyJ..."

# ✅ Devrait retourner l'utilisateur connecté (pas le premier user)
```

### Test 2: Upload CV
```bash
curl -X POST http://localhost:8000/api/v1/users/upload-cv \
  -H "Authorization: Bearer eyJ..." \
  -F "file=@/path/to/cv.pdf"

# ✅ Devrait créer uploads/cv/{user_id}_cv.pdf
# ✅ user.cv_path devrait être mis à jour
```

### Test 3: Update profil
```bash
curl -X PATCH http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{"cover_letter_template":"Mon template..."}'

# ✅ Devrait mettre à jour le template
```

### Test 4: Filtrage job offers
```bash
# Sans filtre
curl http://localhost:8000/api/v1/job-offers/

# Avec filtre user_id
curl http://localhost:8000/api/v1/job-offers/?user_id=1

# ✅ Devrait retourner uniquement les offres du user 1
```

---

## 🚀 Compatibilité Frontend

### Headers requis pour toutes les requêtes authentifiées:
```typescript
headers: {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
}
```

### Endpoints mis à jour:
- ✅ `GET /api/v1/users/me` - Fonctionne maintenant avec JWT
- ✅ `PATCH /api/v1/users/me` - Nouveau
- ✅ `POST /api/v1/users/upload-cv` - Nouveau
- ✅ `GET /api/v1/job-offers/?user_id=X` - Filtrage ajouté

### Schemas TypeScript correspondants:
```typescript
interface User {
  id: number;
  email: string;
  name: string;
  cv_path: string | null;  // ✨ Nouveau
  cover_letter_template: string | null;  // ✨ Nouveau
  created_at: string;
  updated_at: string;
}

interface UserUpdate {
  name?: string;
  email?: string;
  password?: string;
  cv_path?: string;  // ✨ Nouveau
  cover_letter_template?: string;  // ✨ Nouveau
}
```

---

## ✅ Checklist Validation

- [x] Migration Alembic appliquée
- [x] Colonnes cv_path et cover_letter_template dans users
- [x] GET /users/me retourne l'user du token JWT
- [x] POST /users/upload-cv fonctionne
- [x] PATCH /users/me fonctionne
- [x] GET /job-offers/?user_id= filtre correctement
- [x] Schemas Pydantic mis à jour
- [x] Compatible avec frontend existant

---

## 📝 Notes Importantes

1. **Dossier uploads:** Le backend crée automatiquement `uploads/cv/` si inexistant
2. **Validation PDF:** Seuls les fichiers `.pdf` sont acceptés pour le CV
3. **JWT requis:** Tous les nouveaux endpoints nécessitent l'authentification
4. **user_id optionnel:** Le filtrage par user_id est optionnel (pour admins)

---

**Date:** 5 décembre 2025  
**Version:** 1.1.0  
**Status:** ✅ Tous les changements testés et déployés
