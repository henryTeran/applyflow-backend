# 🔧 Patch de Debugging pour le Frontend

## Modifications Recommandées

### 1. QuickApplyPage.tsx - Améliorer le logging

**Avant (lignes ~59-65) :**
```typescript
try {
  const result = await scrapeJobOffer({ url: urlValue });
  // ...
} catch (error) {
  console.log('⚠️ Endpoint /scrape non implémenté - Utilisation de données mock');
}
```

**Après (avec diagnostic détaillé) :**
```typescript
try {
  console.log('📤 Scraping URL:', urlValue);
  
  const result = await scrapeJobOffer({ url: urlValue });
  
  console.log('✅ Scraping réussi:', {
    title: result.title,
    company: result.company,
    location: result.location
  });
  
  // ... reste du code
} catch (error: any) {
  // Logging détaillé de l'erreur
  console.error('❌ Scraping échoué:', {
    status: error.response?.status,
    statusText: error.response?.statusText,
    data: error.response?.data,
    message: error.message
  });
  
  // Différencier les types d'erreurs
  if (error.response?.status === 400) {
    const errorDetail = error.response?.data?.detail;
    
    if (errorDetail?.includes('ChromeDriver')) {
      console.warn('⚠️ ChromeDriver non disponible - Utilisation de données mock');
    } else if (errorDetail?.includes('Platform')) {
      console.warn('⚠️ Plateforme non supportée - Utilisation de données mock');
    } else {
      console.warn('⚠️ Erreur scraping - Utilisation de données mock:', errorDetail);
    }
  } else if (error.response?.status === 422) {
    console.error('❌ URL invalide:', error.response?.data);
    throw new Error('URL invalide. Veuillez vérifier le format.');
  }
  
  // Continuer avec les données mock
  console.log('🔄 Fallback sur données mock');
  // ... code mock existant
}
```

### 2. Vérifier le CV avant l'analyse de match

**Ajouter avant l'appel à `analyzeMatch` (ligne ~119) :**

```typescript
// Vérifier que l'utilisateur a un CV
console.log('🔍 Vérification du CV avant analyse...');

try {
  // Récupérer les infos utilisateur
  const currentUser = await getCurrentUser(); // Vous avez probablement cette fonction
  
  if (!currentUser.cv_text || currentUser.cv_text.trim() === '') {
    console.error('❌ CV manquant - Upload requis');
    toast.error(
      'Veuillez d\'abord uploader votre CV dans votre profil',
      { duration: 5000 }
    );
    return; // Arrêter le processus
  }
  
  console.log('✅ CV présent:', {
    cv_length: currentUser.cv_text.length,
    has_skills: !!currentUser.skills,
    has_experience: !!currentUser.experience
  });
  
} catch (error) {
  console.error('❌ Erreur lors de la vérification du CV:', error);
}

// Puis continuer avec analyzeMatch
console.log('📤 Analyse de match pour job_offer_id:', createdJobOffer.id);

try {
  await analyzeMatch({ jobOfferId: createdJobOffer.id });
  console.log('✅ Analyse de match réussie');
} catch (error: any) {
  console.error('❌ Analyse de match échouée:', {
    status: error.response?.status,
    data: error.response?.data,
    message: error.message
  });
  
  if (error.response?.status === 400) {
    toast.error(
      'Erreur lors de l\'analyse. Vérifiez que votre CV est à jour.',
      { duration: 5000 }
    );
  }
}
```

### 3. Normaliser l'URL avant envoi (optionnel, déjà fait côté backend)

**Si vous voulez normaliser côté frontend aussi :**

```typescript
// Fonction utilitaire à ajouter en haut du fichier
const normalizeUrl = (url: string): string => {
  let normalized = url.trim();
  
  // Ajouter https:// si manquant
  if (!normalized.startsWith('http://') && !normalized.startsWith('https://')) {
    normalized = `https://${normalized}`;
  }
  
  return normalized;
};

// Dans handleScrapeAndProcess
const handleScrapeAndProcess = async () => {
  const normalizedUrl = normalizeUrl(urlValue);
  console.log('🔗 URL normalisée:', normalizedUrl);
  
  try {
    const result = await scrapeJobOffer({ url: normalizedUrl });
    // ...
  } catch (error) {
    // ...
  }
};
```

### 4. Ajouter un indicateur visuel pour le statut du scraping

**Dans le JSX :**

```typescript
const [scrapingStatus, setScrapingStatus] = useState<
  'idle' | 'scraping' | 'success' | 'fallback' | 'error'
>('idle');

// Dans handleScrapeAndProcess
const handleScrapeAndProcess = async () => {
  setScrapingStatus('scraping');
  
  try {
    const result = await scrapeJobOffer({ url: urlValue });
    setScrapingStatus('success');
    // ...
  } catch (error) {
    setScrapingStatus('fallback');
    // ... utiliser mock data
  }
};

// Dans le JSX, afficher un badge
{scrapingStatus === 'fallback' && (
  <div className="text-sm text-yellow-600 mt-2">
    ⚠️ Données de démonstration (scraping temporairement indisponible)
  </div>
)}

{scrapingStatus === 'success' && (
  <div className="text-sm text-green-600 mt-2">
    ✅ Données scrapées avec succès
  </div>
)}
```

## 🧪 Tests à Effectuer

### Test 1 : Vérifier le format des erreurs

**Dans la console du navigateur :**
```javascript
// Tester différentes URLs
const testUrls = [
  'https://www.linkedin.com/jobs/view/123',
  'linkedin.com/jobs/view/123',
  'invalid-url',
  ''
];

for (const url of testUrls) {
  console.log(`\n🧪 Test URL: "${url}"`);
  // Puis soumettre via l'interface
}
```

### Test 2 : Vérifier l'état du CV

**Dans la console du navigateur :**
```javascript
// Vérifier si l'utilisateur a un CV
fetch('http://localhost:8000/api/v1/users/me', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  }
})
  .then(r => r.json())
  .then(user => {
    console.log('👤 Utilisateur:', {
      email: user.email,
      has_cv: !!user.cv_text,
      cv_length: user.cv_text?.length,
      has_skills: !!user.skills,
      has_experience: !!user.experience
    });
  });
```

### Test 3 : Upload d'un CV de test

**Créer un fichier CV simple :**
```
John Doe
Senior Full Stack Developer

COMPÉTENCES:
- Python, FastAPI, React, TypeScript
- PostgreSQL, Redis, Docker
- AWS, CI/CD, Git

EXPÉRIENCE:
- 5 ans développement web
- Architecture microservices
- Leadership technique
```

**L'uploader via l'interface ou :**
```javascript
const fileInput = document.querySelector('input[type="file"]');
const file = fileInput.files[0];

const formData = new FormData();
formData.append('file', file);

fetch('http://localhost:8000/api/v1/users/cv', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  },
  body: formData
})
  .then(r => r.json())
  .then(console.log);
```

## 📋 Checklist de Validation

Après application du patch :

- [ ] Les logs montrent l'URL normalisée
- [ ] Les erreurs 400 affichent les détails (`error.response?.data`)
- [ ] Le fallback sur mock data fonctionne
- [ ] Un message prévient l'utilisateur si le CV est manquant
- [ ] L'analyse de match ne s'exécute que si le CV existe
- [ ] Les statuts de scraping sont visibles dans l'UI

## 🎯 Résultat Attendu

### Console Frontend (succès)
```
📤 Scraping URL: linkedin.com/jobs/view/123
🔗 URL normalisée: https://linkedin.com/jobs/view/123
⚠️ ChromeDriver non disponible - Utilisation de données mock
🔄 Fallback sur données mock
✅ Job offer créé: {id: 7, title: "..."}
🔍 Vérification du CV avant analyse...
✅ CV présent: {cv_length: 1234, has_skills: true}
📤 Analyse de match pour job_offer_id: 7
✅ Analyse de match réussie
```

### Console Frontend (CV manquant)
```
📤 Scraping URL: linkedin.com/jobs/view/123
⚠️ ChromeDriver non disponible - Utilisation de données mock
✅ Job offer créé: {id: 7, title: "..."}
🔍 Vérification du CV avant analyse...
❌ CV manquant - Upload requis
[Toast] Veuillez d'abord uploader votre CV dans votre profil
```

## 🔗 Fichiers de Référence

- `DIAGNOSTIC_FRONTEND.md` - Diagnostic complet des erreurs
- `DEBUG_SCRAPE_400.md` - Guide de debugging backend
- `CORRECTION_SCRAPE_400.md` - Documentation de la fix backend
- `TROUBLESHOOTING_SCRAPE.md` - Troubleshooting général

## 💡 Notes Importantes

1. **Le backend accepte déjà les URLs avec/sans https://** - La normalisation côté frontend est optionnelle
2. **ChromeDriver est un problème d'infrastructure WSL** - Pas un bug frontend
3. **Les données mock sont une solution valide** - Permet de continuer le développement
4. **L'upload de CV est prioritaire** - Requis pour l'analyse de match

## 📞 Support Technique

Si après application du patch les erreurs persistent :

1. Vérifiez que le backend est bien démarré (port 8000)
2. Vérifiez les logs backend pour voir les requêtes
3. Utilisez les outils de dev Chrome (Network tab)
4. Partagez les logs complets de la console

---

**Dernière mise à jour :** 5 décembre 2025  
**Version backend :** 1.0.0  
**Status :** ChromeDriver en cours de fix (bibliothèques WSL)
