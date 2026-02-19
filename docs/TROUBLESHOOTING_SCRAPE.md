# 🚨 TROUBLESHOOTING IMMÉDIAT - Erreur 400 /scrape

**Status:** Erreur toujours présente après modifications  
**Action requise:** **REDÉMARRER LE SERVEUR BACKEND** 🔄

---

## ⚠️ PROBLÈME ACTUEL

L'erreur 400 persiste car **le serveur backend n'a pas été redémarré** avec les nouvelles modifications.

```
POST http://localhost:8000/api/v1/job-offers/scrape 400 (Bad Request)
```

---

## ✅ SOLUTION IMMÉDIATE (3 ÉTAPES)

### Étape 1: Arrêter le serveur actuel

Dans le terminal où tourne le serveur backend :
```bash
# Appuyez sur Ctrl+C
```

---

### Étape 2: Relancer le serveur

```bash
cd /mnt/c/projets/ApplyFlow/backend
uvicorn app.main:app --reload --port 8000
```

**Attendez de voir:**
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

---

### Étape 3: Vérifier que les modifications sont chargées

Dans un **autre terminal**, testez l'endpoint :

```bash
# Test rapide (devrait maintenant accepter les URLs sans https://)
curl -X POST http://localhost:8000/api/v1/job-offers/scrape \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "linkedin.com/jobs/view/123"}' \
  -v
```

**Si vous voyez `422` au lieu de `400`**, c'est bon signe ! Ça veut dire que le validateur custom fonctionne.

---

## 🔍 DIAGNOSTIC DÉTAILLÉ

### Obtenir le message d'erreur exact

**Dans QuickApplyPage.tsx, modifiez temporairement le catch:**

```typescript
try {
  const { data } = await apiClient.post('/job-offers/scrape', {
    url: jobUrl
  });
  // ...
} catch (error: any) {
  // 🔍 AJOUTEZ CES LOGS POUR DEBUG
  console.error('❌ Full error:', error);
  console.error('❌ Response data:', error.response?.data);
  console.error('❌ Response status:', error.response?.status);
  console.error('❌ URL sent:', jobUrl);
  
  setError(error.response?.data?.detail || 'Erreur lors du scraping');
}
```

**Testez à nouveau et regardez la console du navigateur.** Vous devriez voir :

```javascript
❌ Response data: { detail: "..." }  // Message d'erreur exact
❌ Response status: 400
❌ URL sent: "..."  // L'URL que vous avez saisie
```

---

## 🎯 CAUSES POSSIBLES (après redémarrage)

### Cause 1: URL sans https:// et serveur pas redémarré

**Symptôme:** Erreur 422 Unprocessable Entity

**Solution:** Redémarrer le serveur (voir Étape 1-2 ci-dessus)

---

### Cause 2: Plateforme non supportée

**Symptôme:** 
```json
{ "detail": "Platform not supported. Supported platforms: LinkedIn, Indeed, Welcome to the Jungle." }
```

**Solution:** Utilisez une URL contenant :
- `linkedin.com`
- `indeed.com` / `indeed.fr`
- `welcometothejungle.com`

---

### Cause 3: Selenium non installé

**Symptôme:**
```json
{ "detail": "Failed to scrape job offer: 'chromedriver' executable needs to be in PATH..." }
```

**Solution:**
```bash
cd /mnt/c/projets/ApplyFlow/backend
pip install selenium==4.16.0 webdriver-manager==4.0.1
```

Puis redémarrer le serveur.

---

### Cause 4: URL n'existe pas

**Symptôme:**
```json
{ "detail": "Failed to scrape job offer: Message: timeout..." }
```

**Solution:** Utilisez une vraie URL LinkedIn existante pour tester.

---

## 🧪 TEST AVEC UNE VRAIE URL

**Testez avec cette URL LinkedIn (si elle existe encore) :**

```
https://www.linkedin.com/jobs/view/3787654321/
```

Ou trouvez une vraie offre sur LinkedIn et copiez son URL.

---

## 📋 CHECKLIST DE VÉRIFICATION

- [ ] **Serveur backend redémarré** avec `uvicorn app.main:app --reload`
- [ ] **Logs backend visibles** dans le terminal
- [ ] **Console frontend ouverte** (F12 dans Chrome)
- [ ] **Logs détaillés ajoutés** dans le catch (voir ci-dessus)
- [ ] **URL testée est valide** (vraie offre LinkedIn/Indeed/WTTJ)
- [ ] **Token valide** (pas expiré)

---

## 🔧 COMMANDES DE TEST RAPIDE

### Test 1: Vérifier que le serveur tourne

```bash
curl http://localhost:8000/docs
# Devrait retourner du HTML (page Swagger)
```

---

### Test 2: Vérifier l'authentification

```bash
# Se connecter
curl -X POST http://localhost:8000/api/v1/auth/login \
  -F "username=test@example.com" \
  -F "password=test123"

# Devrait retourner:
# { "access_token": "eyJ...", "token_type": "bearer" }
```

---

### Test 3: Tester le scraping avec token

```bash
# 1. Obtenir un token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -F "username=test@example.com" \
  -F "password=test123" \
  | jq -r '.access_token')

# 2. Tester le scraping
curl -X POST http://localhost:8000/api/v1/job-offers/scrape \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "linkedin.com/jobs/view/123"}' \
  | jq

# 3. Observer la réponse
# - Si 200 + JSON avec title/company/etc. → ✅ Succès
# - Si 400 + {"detail": "Platform not supported"} → URL non supportée
# - Si 400 + {"detail": "Failed to scrape..."} → Problème Selenium ou URL invalide
# - Si 422 + validation error → Serveur pas redémarré
```

---

## 📊 MATRICE DE DIAGNOSTIC

| Code | Message | Cause | Solution |
|------|---------|-------|----------|
| 422 | Validation error | Serveur pas redémarré | Redémarrer le serveur |
| 400 | Platform not supported | URL non LinkedIn/Indeed/WTTJ | Changer l'URL |
| 400 | Failed to scrape... chromedriver | Selenium manquant | `pip install selenium webdriver-manager` |
| 400 | Failed to scrape... timeout | URL invalide ou réseau | Tester avec vraie URL |
| 401 | Unauthorized | Token invalide/expiré | Se reconnecter |
| 200 | Données JSON | ✅ Fonctionne ! | - |

---

## 🚀 ÉTAPES SUIVANTES

### 1. **REDÉMARRER LE SERVEUR MAINTENANT**

```bash
# Terminal backend
cd /mnt/c/projets/ApplyFlow/backend
# Ctrl+C si le serveur tourne
uvicorn app.main:app --reload --port 8000
```

---

### 2. **AJOUTER LES LOGS DÉTAILLÉS FRONTEND**

```typescript
// QuickApplyPage.tsx
catch (error: any) {
  console.error('❌ Full error:', error);
  console.error('❌ Response:', error.response?.data);
  console.error('❌ URL sent:', jobUrl);
  setError(error.response?.data?.detail || 'Erreur');
}
```

---

### 3. **TESTER AVEC UNE VRAIE URL**

Allez sur LinkedIn, trouvez une vraie offre, copiez l'URL complète.

Exemple : `https://www.linkedin.com/jobs/view/4079886035/`

---

### 4. **REGARDER LES LOGS BACKEND**

Dans le terminal backend, vous devriez voir :

```
INFO: Scraping request from user 1: https://linkedin.com/jobs/view/123
```

Si vous ne voyez PAS ce log → Le serveur n'a pas les nouvelles modifications.

---

## 💡 SOLUTION LA PLUS PROBABLE

**Le serveur backend n'a pas été redémarré.**

1. Ctrl+C dans le terminal backend
2. `uvicorn app.main:app --reload --port 8000`
3. Retester depuis le frontend

**Si ça ne marche toujours pas**, envoyez-moi :
- Les logs backend (terminal où tourne uvicorn)
- Les logs frontend (console du navigateur avec les logs détaillés)
- L'URL que vous testez

---

## 📞 BESOIN D'AIDE ?

Si après redémarrage l'erreur persiste, partagez :

```
1. Logs backend complets (copier-coller du terminal)
2. Console frontend (copier-coller avec les logs détaillés)
3. L'URL exacte testée
4. La commande utilisée pour démarrer le serveur
```

Je pourrai alors diagnostiquer précisément le problème.
