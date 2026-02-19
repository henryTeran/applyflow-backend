# 🔍 Diagnostic Frontend - Erreurs 400

## Erreurs Observées

### 1. POST /api/v1/job-offers/scrape 400 ❌
```
POST http://localhost:8000/api/v1/job-offers/scrape 400 (Bad Request)
⚠️ Endpoint /scrape non implémenté - Utilisation de données mock
```

**Cause probable :** ChromeDriver ne peut pas s'exécuter sous WSL (status code 127)

**Solution temporaire :** Le frontend utilise déjà des données mock en fallback ✅

**Solution permanente :** Installer les bibliothèques système manquantes :
```bash
sudo apt-get update
sudo apt-get install -y \
  libnss3 libgconf-2-4 libfontconfig1 \
  libxss1 libappindicator3-1 libasound2 \
  libatk-bridge2.0-0 libgtk-3-0 libgbm1
```

### 2. POST /api/v1/job-matches/analyze/7 400 ❌
```
POST http://localhost:8000/api/v1/job-matches/analyze/7 400 (Bad Request)
```

**Cause probable :** L'utilisateur n'a pas encore uploadé de CV

**Solution :** L'utilisateur doit d'abord uploader son CV via `/api/v1/users/cv`

## 📋 Checklist de Diagnostic

### Vérifier les données envoyées par le frontend

Ajoutez dans `QuickApplyPage.tsx` avant l'appel API :

```typescript
// Dans handleScrapeAndProcess, avant l'appel scrape
console.log('📤 Données envoyées à /scrape:', { url: urlValue });

try {
  const result = await scrapeJobOffer({ url: urlValue });
  console.log('✅ Résultat /scrape:', result);
} catch (error) {
  console.error('❌ Erreur /scrape:', error.response?.data);
}
```

### Vérifier que l'utilisateur a un CV

```typescript
// Avant l'analyse de match
const user = await getCurrentUser();
console.log('👤 Utilisateur:', {
  id: user.id,
  has_cv: !!user.cv_text,
  cv_length: user.cv_text?.length
});

if (!user.cv_text) {
  console.warn('⚠️ CV manquant - Upload requis');
  // Rediriger vers la page de profil
}
```

## 🧪 Tests Recommandés

### 1. Tester l'upload de CV

```typescript
const formData = new FormData();
formData.append('file', cvFile);

const response = await fetch('http://localhost:8000/api/v1/users/cv', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});

console.log('CV upload:', await response.json());
```

### 2. Tester le scraping avec URL complète

```typescript
const testUrls = [
  'https://www.linkedin.com/jobs/view/123',
  'linkedin.com/jobs/view/123', // Sans https://
  'www.linkedin.com/jobs/view/123' // Sans protocole
];

for (const url of testUrls) {
  try {
    const result = await scrapeJobOffer({ url });
    console.log(`✅ ${url}:`, result);
  } catch (error) {
    console.error(`❌ ${url}:`, error.response?.data);
  }
}
```

## 🔧 Solutions Immédiates

### Option 1 : Utiliser les données mock (ACTUEL)
Le frontend utilise déjà des données mock en fallback ✅

**Avantage :** Permet de continuer le développement
**Inconvénient :** Pas de vraies données scrapées

### Option 2 : Créer manuellement les job offers
Utiliser l'endpoint `POST /api/v1/job-offers/` avec les données manuelles :

```typescript
const manualJobOffer = {
  title: "Senior Full Stack Developer",
  company: "Tech Corp",
  location: "Paris, France",
  description: "...",
  source: "LinkedIn",
  application_url: "https://www.linkedin.com/jobs/view/123"
};

const result = await createJobOffer(manualJobOffer);
```

### Option 3 : Fixer ChromeDriver (RECOMMANDÉ pour production)

1. Installer les dépendances système :
```bash
sudo apt-get install -y \
  libnss3 libgconf-2-4 libfontconfig1 \
  libxss1 libappindicator3-1 libasound2 \
  libatk-bridge2.0-0 libgtk-3-0 libgbm1
```

2. Ou utiliser Docker (Chrome inclus) :
```bash
docker-compose up -d
```

## 📊 État Actuel

| Feature | Status | Note |
|---------|--------|------|
| URL Validation | ✅ Fixé | Accepte URLs avec/sans https:// |
| Logging | ✅ Actif | Logs détaillés visibles |
| ChromeDriver | ❌ Incompatible | Status 127 sous WSL |
| Mock Fallback | ✅ Actif | Frontend utilise mock data |
| CV Upload | ⚠️ À tester | Endpoint existe, à utiliser |
| Match Analysis | ⚠️ Requis CV | Fonctionne si CV présent |

## 🎯 Prochaines Étapes

1. **Court terme (Développement frontend) :**
   - ✅ Continuer avec les données mock
   - ✅ Tester la création manuelle de job offers
   - 🔲 Implémenter l'upload de CV dans le frontend

2. **Moyen terme (Scraping fonctionnel) :**
   - 🔲 Installer les bibliothèques système WSL
   - 🔲 Tester ChromeDriver après installation
   - 🔲 Valider le scraping end-to-end

3. **Long terme (Production) :**
   - 🔲 Utiliser Docker pour ChromeDriver
   - 🔲 Rate limiting sur /scrape (10/minute)
   - 🔲 Cache Redis pour les résultats scrapés

## 💡 Conseils

- **Ne bloquez pas le développement frontend** : Les données mock sont suffisantes
- **Testez l'upload de CV** : C'est requis pour l'analyse de match
- **ChromeDriver peut attendre** : C'est une amélioration, pas un bloqueur
- **Utilisez les logs** : `console.log(error.response?.data)` montre les vraies erreurs

## 📞 Support

Si les erreurs persistent après l'upload du CV, vérifiez :
1. Le token JWT est valide (`Authorization: Bearer <token>`)
2. Le serveur backend est démarré (port 8000)
3. Les logs backend montrent les requêtes entrantes
4. Le CORS est configuré (déjà fait normalement)
