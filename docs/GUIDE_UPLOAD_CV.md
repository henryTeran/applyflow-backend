# 📤 Guide d'Upload de CV - Débloquer l'Analyse de Match

## 🎯 Objectif

L'endpoint `/api/v1/job-matches/analyze/{job_offer_id}` requiert que l'utilisateur ait uploadé un CV. Ce guide montre comment implémenter et tester l'upload de CV.

---

## 🚨 Symptôme

**Erreur Frontend:**
```
POST http://localhost:8000/api/v1/job-matches/analyze/7 400 (Bad Request)
```

**Cause:**
```json
{
  "detail": "User must upload CV before analyzing job matches"
}
```

**Solution:** Uploader un CV avant d'utiliser l'analyse de match.

---

## 🔧 Backend - Endpoint d'Upload

### POST /api/v1/users/cv

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: multipart/form-data
```

**Body (form-data):**
```
file: <fichier PDF, DOCX, ou TXT>
```

**Réponse Success (200):**
```json
{
  "id": 9,
  "email": "user@example.com",
  "full_name": "John Doe",
  "cv_text": "John Doe\nSenior Full Stack Developer\n\nCOMPÉTENCES:\n- Python...",
  "skills": "Python, FastAPI, React, TypeScript, PostgreSQL",
  "experience": "5 years in web development...",
  "cv_file_path": "/uploads/cv/user_9_cv.pdf",
  "created_at": "2025-12-05T14:30:00",
  "updated_at": "2025-12-05T14:30:00"
}
```

**Réponse Error (400):**
```json
{
  "detail": "Unsupported file format. Please upload PDF, DOCX, or TXT."
}
```

---

## 💻 Frontend - Implémentation React

### 1. Composant d'Upload Simple

```typescript
// components/CVUpload.tsx
import { useState } from 'react';
import { useToast } from '@/hooks/use-toast';

export const CVUpload = () => {
  const [isUploading, setIsUploading] = useState(false);
  const { toast } = useToast();

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validation du format
    const allowedTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain'
    ];

    if (!allowedTypes.includes(file.type)) {
      toast({
        title: 'Format non supporté',
        description: 'Veuillez uploader un fichier PDF, DOCX ou TXT.',
        variant: 'destructive'
      });
      return;
    }

    // Validation de la taille (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      toast({
        title: 'Fichier trop volumineux',
        description: 'La taille maximale est de 10MB.',
        variant: 'destructive'
      });
      return;
    }

    setIsUploading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/users/cv', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Upload failed');
      }

      const user = await response.json();

      toast({
        title: 'CV uploadé avec succès',
        description: `${user.cv_text.substring(0, 100)}...`,
        variant: 'success'
      });

      console.log('✅ CV uploadé:', {
        cv_length: user.cv_text.length,
        skills: user.skills,
        experience_length: user.experience?.length
      });

      // Optionnel: recharger les données utilisateur
      // await refetchUser();

    } catch (error: any) {
      console.error('❌ Upload CV failed:', error);
      toast({
        title: 'Erreur d\'upload',
        description: error.message,
        variant: 'destructive'
      });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="space-y-4">
      <label
        htmlFor="cv-upload"
        className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-lg cursor-pointer hover:bg-gray-50"
      >
        <div className="flex flex-col items-center justify-center pt-5 pb-6">
          <svg className="w-10 h-10 mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <p className="mb-2 text-sm text-gray-500">
            {isUploading ? (
              <span className="font-semibold">Upload en cours...</span>
            ) : (
              <>
                <span className="font-semibold">Cliquez pour uploader</span> ou glissez-déposez
              </>
            )}
          </p>
          <p className="text-xs text-gray-500">PDF, DOCX ou TXT (max. 10MB)</p>
        </div>
        <input
          id="cv-upload"
          type="file"
          className="hidden"
          accept=".pdf,.docx,.txt"
          onChange={handleUpload}
          disabled={isUploading}
        />
      </label>
    </div>
  );
};
```

### 2. Intégration dans QuickApplyPage

```typescript
// QuickApplyPage.tsx
import { CVUpload } from '@/components/CVUpload';
import { useState, useEffect } from 'react';

export const QuickApplyPage = () => {
  const [userHasCV, setUserHasCV] = useState(false);
  
  // Vérifier si l'utilisateur a un CV au chargement
  useEffect(() => {
    checkUserCV();
  }, []);

  const checkUserCV = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/users/me', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      const user = await response.json();
      setUserHasCV(!!user.cv_text && user.cv_text.trim() !== '');
      
      console.log('👤 CV Status:', {
        has_cv: !!user.cv_text,
        cv_length: user.cv_text?.length,
        skills: user.skills
      });
    } catch (error) {
      console.error('❌ Failed to check CV:', error);
    }
  };

  const handleScrapeAndProcess = async () => {
    // ... scraping code ...

    // Avant l'analyse de match
    if (!userHasCV) {
      toast({
        title: 'CV requis',
        description: 'Veuillez uploader votre CV avant d\'utiliser l\'analyse de match.',
        variant: 'warning',
        action: (
          <Button onClick={() => navigate('/profile')}>
            Aller au profil
          </Button>
        )
      });
      return;
    }

    // Puis continuer avec l'analyse
    try {
      await analyzeMatch({ jobOfferId: createdJobOffer.id });
      console.log('✅ Analyse de match réussie');
    } catch (error) {
      console.error('❌ Analyse échouée:', error);
    }
  };

  return (
    <div>
      {/* Afficher l'upload CV si nécessaire */}
      {!userHasCV && (
        <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <h3 className="text-lg font-semibold mb-2">
            📤 CV Requis pour l'Analyse de Match
          </h3>
          <p className="text-sm text-gray-600 mb-4">
            Pour utiliser l'analyse automatique de match, veuillez d'abord uploader votre CV.
          </p>
          <CVUpload />
        </div>
      )}

      {/* ... reste du code ... */}
    </div>
  );
};
```

### 3. API Client Helper

```typescript
// api/users.ts
export const uploadCV = async (file: File): Promise<User> => {
  const formData = new FormData();
  formData.append('file', file);

  const token = localStorage.getItem('token');
  const response = await fetch(`${API_BASE_URL}/users/cv`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }

  return response.json();
};

export const getCurrentUser = async (): Promise<User> => {
  const token = localStorage.getItem('token');
  const response = await fetch(`${API_BASE_URL}/users/me`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  if (!response.ok) {
    throw new Error('Failed to fetch user');
  }

  return response.json();
};
```

---

## 🧪 Tests

### Test 1: Upload via cURL

```bash
# 1. Créer un fichier CV de test
cat > test_cv.txt << 'EOF'
John Doe
Senior Full Stack Developer
john.doe@example.com
+33 6 12 34 56 78

COMPÉTENCES:
- Python, FastAPI, SQLAlchemy
- React, TypeScript, Next.js
- PostgreSQL, Redis, Docker
- AWS, CI/CD, Git

EXPÉRIENCE:
Senior Developer @ TechCorp (2020-2025)
- Architecture microservices
- Leadership technique
- Mentorat juniors

FORMATION:
Master Informatique - Université Paris (2018)
EOF

# 2. Obtenir le token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=password123" | jq -r .access_token)

echo "Token: $TOKEN"

# 3. Uploader le CV
curl -X POST http://localhost:8000/api/v1/users/cv \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test_cv.txt" | jq

# Résultat attendu:
# {
#   "id": 9,
#   "email": "test@example.com",
#   "cv_text": "John Doe\nSenior Full Stack Developer...",
#   "skills": "Python, FastAPI, React, TypeScript, PostgreSQL",
#   "experience": "5 years in web development...",
#   "cv_file_path": "/uploads/cv/user_9_cv.txt"
# }
```

### Test 2: Vérifier le CV

```bash
# Récupérer les infos utilisateur
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN" | jq '{
    email: .email,
    has_cv: (.cv_text != null),
    cv_length: (.cv_text | length),
    skills: .skills
  }'

# Résultat attendu:
# {
#   "email": "test@example.com",
#   "has_cv": true,
#   "cv_length": 456,
#   "skills": "Python, FastAPI, React, TypeScript, PostgreSQL"
# }
```

### Test 3: Tester l'Analyse de Match (après upload)

```bash
# 1. Créer un job offer
JOB_ID=$(curl -s -X POST http://localhost:8000/api/v1/job-offers/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Full Stack Developer",
    "company": "TechCorp",
    "location": "Paris, France",
    "description": "Looking for a senior full stack developer with Python, React, and PostgreSQL experience.",
    "source": "LinkedIn",
    "application_url": "https://www.linkedin.com/jobs/view/123"
  }' | jq -r .id)

echo "Job Offer ID: $JOB_ID"

# 2. Analyser le match
curl -X POST "http://localhost:8000/api/v1/job-matches/analyze/$JOB_ID" \
  -H "Authorization: Bearer $TOKEN" | jq

# Résultat attendu (avec CV):
# {
#   "id": 1,
#   "job_offer_id": 7,
#   "user_id": 9,
#   "match_score": 85,
#   "strengths": ["Python experience", "React skills", "PostgreSQL"],
#   "weaknesses": ["No AWS certification mentioned"],
#   "suggestions": ["Consider highlighting cloud experience"],
#   "created_at": "2025-12-05T14:30:00"
# }

# Résultat attendu (sans CV):
# {
#   "detail": "User must upload CV before analyzing job matches"
# }
```

---

## 📊 Formats de CV Supportés

| Format | Extension | MIME Type | Support |
|--------|-----------|-----------|---------|
| PDF | `.pdf` | `application/pdf` | ✅ Oui |
| Word | `.docx` | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` | ✅ Oui |
| Texte | `.txt` | `text/plain` | ✅ Oui |
| Word 97-2003 | `.doc` | `application/msword` | ❌ Non supporté |

---

## 🔍 Extraction de Données du CV

Le backend extrait automatiquement :

1. **cv_text** - Texte complet du CV
2. **skills** - Compétences techniques détectées
3. **experience** - Résumé de l'expérience
4. **cv_file_path** - Chemin du fichier uploadé

**Algorithme d'extraction:**
```python
# Backend: app/api/v1/users.py
def extract_cv_data(file_content: str):
    # 1. Extraction du texte complet
    cv_text = clean_text(file_content)
    
    # 2. Détection des compétences (mots-clés techniques)
    skills = extract_skills(cv_text)
    
    # 3. Résumé de l'expérience
    experience = summarize_experience(cv_text)
    
    return {
        "cv_text": cv_text,
        "skills": skills,
        "experience": experience
    }
```

---

## ✅ Checklist d'Implémentation

### Backend (déjà fait ✅)
- [x] Endpoint POST /users/cv
- [x] Validation format fichier
- [x] Extraction texte (PDF, DOCX, TXT)
- [x] Stockage dans la DB (champ `cv_text`)
- [x] Extraction skills et experience
- [x] Vérification CV avant analyse de match

### Frontend (à implémenter)
- [ ] Composant CVUpload créé
- [ ] Validation format côté client
- [ ] Gestion des erreurs d'upload
- [ ] Affichage du statut CV (uploaded/missing)
- [ ] Vérification CV avant Quick Apply
- [ ] Redirection vers profil si CV manquant

---

## 🐛 Troubleshooting

### Erreur: "Unsupported file format"

**Cause:** Le fichier n'est pas PDF, DOCX ou TXT

**Solution:**
```typescript
const allowedTypes = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'text/plain'
];

if (!allowedTypes.includes(file.type)) {
  console.error('Format non supporté:', file.type);
}
```

### Erreur: "File too large"

**Cause:** Le fichier dépasse 10MB

**Solution:**
```typescript
const MAX_SIZE = 10 * 1024 * 1024; // 10MB

if (file.size > MAX_SIZE) {
  toast.error('Fichier trop volumineux (max 10MB)');
}
```

### Erreur: "User must upload CV"

**Cause:** L'utilisateur n'a pas encore uploadé de CV

**Solution:**
```typescript
const user = await getCurrentUser();

if (!user.cv_text) {
  toast.warning('Veuillez d\'abord uploader votre CV');
  navigate('/profile');
}
```

---

## 🔗 Fichiers de Référence

- **Backend:** `app/api/v1/users.py` - Endpoint d'upload
- **Models:** `app/models/user.py` - Champs CV (cv_text, skills, experience)
- **Schemas:** `app/schemas/user.py` - Validation upload
- **Frontend:** `FRONTEND_DEBUG_PATCH.md` - Patch de logging
- **Status:** `STATUS_ERREURS_400.md` - Status complet des erreurs

---

**Dernière mise à jour:** 5 décembre 2025  
**Version backend:** 1.0.0  
**Endpoint:** `POST /api/v1/users/cv`  
**Status:** ✅ Prêt à l'emploi
