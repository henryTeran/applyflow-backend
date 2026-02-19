# 🔧 DEBUG: Erreur 400 sur /scrape

**Date:** 5 décembre 2025  
**Erreur:** `POST http://localhost:8000/api/v1/job-offers/scrape 400 (Bad Request)`

---

## 🔍 DIAGNOSTIC

### Causes possibles de l'erreur 400

L'endpoint `/scrape` retourne une erreur 400 dans 3 cas :

#### 1. **Format d'URL invalide** (le plus probable ⚠️)

Le backend utilise `HttpUrl` de Pydantic qui est très strict sur le format.

**Problème courant :**
```typescript
// ❌ INVALIDE - URL incomplète
{ "url": "linkedin.com/jobs/view/123" }
{ "url": "www.linkedin.com/jobs/view/123" }

// ✅ VALIDE - URL complète avec protocole
{ "url": "https://www.linkedin.com/jobs/view/123" }
{ "url": "https://linkedin.com/jobs/view/123" }
```

**Solution Frontend :**
```typescript
// Normaliser l'URL avant l'envoi
const normalizeUrl = (url: string): string => {
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    return `https://${url}`;
  }
  return url;
};

// Utilisation
const response = await apiClient.post('/job-offers/scrape', {
  url: normalizeUrl(jobUrl)
});
```

---

#### 2. **Plateforme non supportée**

```json
// Réponse si la plateforme n'est pas LinkedIn, Indeed ou WTTJ
{
  "detail": "Platform not supported. Supported platforms: LinkedIn, Indeed, Welcome to the Jungle."
}
```

**Plateformes supportées :**
- ✅ `linkedin.com`
- ✅ `indeed.com` / `indeed.fr` / `indeed.co.uk` etc.
- ✅ `welcometothejungle.com`

---

#### 3. **Échec du scraping**

```json
{
  "detail": "Failed to scrape job offer: [message d'erreur]"
}
```

Peut arriver si :
- L'URL n'existe pas (404)
- LinkedIn bloque le scraping (anti-bot)
- Timeout (>10 secondes)
- Selenium/ChromeDriver non installé

---

## 🧪 TESTS DE DIAGNOSTIC

### Test 1: Vérifier le format exact envoyé

**Dans le frontend (QuickApplyPage.tsx) :**

```typescript
// Ajouter un console.log avant l'appel API
console.log('📤 Scraping request:', {
  url: jobUrl,
  normalized: normalizeUrl(jobUrl)
});

try {
  const response = await apiClient.post('/job-offers/scrape', {
    url: normalizeUrl(jobUrl)
  });
  console.log('✅ Scraping response:', response.data);
} catch (error) {
  console.error('❌ Scraping error:', error.response?.data);
}
```

---

### Test 2: Tester directement avec curl

```bash
# Obtenir un token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -F "username=test@example.com" \
  -F "password=test123" \
  | jq -r '.access_token')

# Test 1: URL complète avec https (devrait marcher)
curl -X POST http://localhost:8000/api/v1/job-offers/scrape \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.linkedin.com/jobs/view/3787654321/"}' \
  -v

# Test 2: URL sans https (devrait échouer avec 422)
curl -X POST http://localhost:8000/api/v1/job-offers/scrape \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "linkedin.com/jobs/view/123"}' \
  -v

# Test 3: URL invalide (devrait échouer avec 422)
curl -X POST http://localhost:8000/api/v1/job-offers/scrape \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "not-a-url"}' \
  -v
```

---

### Test 3: Vérifier les logs backend

```bash
# Dans le terminal où tourne uvicorn
# Regarder les logs pour voir l'erreur exacte
```

Si vous voyez :
- `422 Unprocessable Entity` → Format d'URL invalide (validation Pydantic)
- `400 Bad Request` → Plateforme non supportée OU scraping échoué

---

## 🔧 SOLUTIONS

### Solution 1: Normaliser l'URL côté frontend (RECOMMANDÉ)

**Fichier:** `QuickApplyPage.tsx` (ou `apiClient.ts`)

```typescript
// Fonction utilitaire
const normalizeJobUrl = (url: string): string => {
  // Enlever les espaces
  url = url.trim();
  
  // Ajouter https:// si manquant
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    url = `https://${url}`;
  }
  
  return url;
};

// Utilisation dans handleQuickApply
const handleQuickApply = async () => {
  try {
    setIsLoading(true);
    
    const normalizedUrl = normalizeJobUrl(jobUrl);
    console.log('🔗 Normalized URL:', normalizedUrl);
    
    const { data } = await apiClient.post('/job-offers/scrape', {
      url: normalizedUrl
    });
    
    // ... reste du code
  } catch (error) {
    console.error('❌ Error details:', error.response?.data);
    // ...
  }
};
```

---

### Solution 2: Assouplir la validation côté backend (ALTERNATIVE)

Si vous voulez que le backend accepte des URLs sans protocole :

**Fichier:** `app/api/v1/job_offers.py`

```python
from pydantic import BaseModel, field_validator

class ScrapeRequest(BaseModel):
    """Request to scrape a job offer URL"""
    url: str  # Changé de HttpUrl à str
    
    @field_validator('url')
    @classmethod
    def normalize_url(cls, v: str) -> str:
        """Normalize URL by adding https:// if missing"""
        v = v.strip()
        if not v.startswith(('http://', 'https://')):
            v = f'https://{v}'
        return v
```

---

### Solution 3: Validation côté frontend avec feedback

**Fichier:** `QuickApplyPage.tsx`

```typescript
const [urlError, setUrlError] = useState<string>('');

const validateUrl = (url: string): boolean => {
  setUrlError('');
  
  if (!url.trim()) {
    setUrlError('URL requise');
    return false;
  }
  
  // Vérifier qu'au moins un domaine est présent
  if (!url.includes('.')) {
    setUrlError('URL invalide');
    return false;
  }
  
  // Vérifier plateforme supportée
  const supportedPlatforms = ['linkedin.com', 'indeed.com', 'indeed.fr', 'welcometothejungle.com'];
  const isSupported = supportedPlatforms.some(platform => url.includes(platform));
  
  if (!isSupported) {
    setUrlError('Plateforme non supportée. Utilisez LinkedIn, Indeed ou Welcome to the Jungle.');
    return false;
  }
  
  return true;
};

const handleQuickApply = async () => {
  if (!validateUrl(jobUrl)) {
    return;
  }
  
  // ... reste du code
};

// Dans le JSX
<TextField
  label="URL de l'offre"
  value={jobUrl}
  onChange={(e) => setJobUrl(e.target.value)}
  error={!!urlError}
  helperText={urlError || 'LinkedIn, Indeed ou Welcome to the Jungle'}
/>
```

---

## 📋 CHECKLIST DE DEBUG

1. **Vérifier la requête envoyée**
   ```typescript
   console.log('Request:', { url: jobUrl });
   ```

2. **Vérifier la réponse d'erreur**
   ```typescript
   console.error('Error response:', error.response?.data);
   console.error('Status code:', error.response?.status);
   ```

3. **Tester avec une URL LinkedIn valide**
   ```
   https://www.linkedin.com/jobs/view/3787654321/
   ```

4. **Vérifier que le token est valide**
   ```typescript
   console.log('Token:', localStorage.getItem('token')?.substring(0, 20) + '...');
   ```

5. **Vérifier les logs backend**
   - Regarder la console où tourne `uvicorn`
   - Chercher l'erreur exacte

---

## 🎯 SOLUTION RAPIDE (COPY-PASTE)

**1. Ajouter cette fonction dans `QuickApplyPage.tsx` :**

```typescript
const normalizeJobUrl = (url: string): string => {
  url = url.trim();
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    return `https://${url}`;
  }
  return url;
};
```

**2. Modifier l'appel API :**

```typescript
const handleQuickApply = async () => {
  try {
    setIsLoading(true);
    setError(null);
    
    // Normaliser l'URL
    const normalizedUrl = normalizeJobUrl(jobUrl);
    
    // Scraper
    const { data } = await apiClient.post('/job-offers/scrape', {
      url: normalizedUrl
    });
    
    // ... reste du code
  } catch (error: any) {
    console.error('Quick apply error:', error.response?.data);
    setError(error.response?.data?.detail || 'Erreur lors du scraping');
  } finally {
    setIsLoading(false);
  }
};
```

**3. Tester avec :**
```
linkedin.com/jobs/view/123
https://www.linkedin.com/jobs/view/123
```

Les deux devraient maintenant fonctionner.

---

## 📞 BESOIN D'AIDE ?

Si l'erreur persiste après ces corrections, envoyez-moi :

1. **La requête exacte envoyée** (console.log avant l'appel API)
2. **La réponse d'erreur complète** (error.response?.data)
3. **L'URL que vous essayez de scraper**
4. **Les logs backend** (console où tourne uvicorn)

---

## ✅ TEST FINAL

```bash
# Backend doit tourner
uvicorn app.main:app --reload

# Dans un autre terminal
TOKEN="votre_token_ici"

# Devrait marcher
curl -X POST http://localhost:8000/api/v1/job-offers/scrape \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.linkedin.com/jobs/view/3787654321/"}' | jq

# Devrait retourner quelque chose comme:
# {
#   "title": "...",
#   "company": "...",
#   "description": "...",
#   "application_type": "portal",
#   "application_url": "https://..."
# }
```
