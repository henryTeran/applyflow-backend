# 🧪 TEST RAPIDE - Endpoint /scrape

**Date:** 5 décembre 2025  
**Status:** ✅ Serveur backend opérationnel  
**Correction:** Validation d'URL appliquée

---

## ⚡ TEST EN 3 COMMANDES

### 1. Créer un compte de test (si nécessaire)

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "scrape-test@example.com",
    "password": "test123",
    "name": "Scrape Test"
  }'
```

**Résultat attendu:**
```json
{
  "id": 1,
  "email": "scrape-test@example.com",
  "name": "Scrape Test",
  ...
}
```

---

### 2. Obtenir un token valide

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -F "username=scrape-test@example.com" \
  -F "password=test123" \
  | jq -r '.access_token')

echo "Token: $TOKEN"
```

**Résultat attendu:**
```
Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

### 3. Tester le scraping (URL SANS https://)

```bash
curl -X POST http://localhost:8000/api/v1/job-offers/scrape \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "linkedin.com/jobs/view/123"}' \
  | jq
```

**Résultat attendu (si l'URL n'existe pas):**
```json
{
  "detail": "Failed to scrape job offer: ..."
}
```

**C'est normal !** L'URL `linkedin.com/jobs/view/123` n'existe probablement pas.

**Important:** Ce qui compte, c'est que vous **ne recevez PAS d'erreur 422** (validation error).

---

## ✅ TEST AVEC UNE VRAIE URL LINKEDIN

### Étape 1: Trouver une vraie offre LinkedIn

1. Allez sur https://www.linkedin.com/jobs
2. Cherchez "développeur" ou "developer"
3. Cliquez sur une offre
4. Copiez l'URL complète (ex: `https://www.linkedin.com/jobs/view/4079886035/`)

---

### Étape 2: Tester avec cette URL

```bash
# Remplacez l'URL par celle que vous avez copiée
curl -X POST http://localhost:8000/api/v1/job-offers/scrape \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.linkedin.com/jobs/view/4079886035/"
  }' \
  | jq
```

**Résultat attendu (succès):**
```json
{
  "title": "Développeur Full Stack Senior",
  "company": "TechCorp",
  "location": "Paris, France",
  "description": "Nous recherchons un développeur...",
  "application_type": "portal",
  "application_url": "https://www.linkedin.com/jobs/view/4079886035/"
}
```

---

## 🎯 TESTS DE VALIDATION

### Test 1: URL sans https:// (devrait marcher maintenant)

```bash
curl -X POST http://localhost:8000/api/v1/job-offers/scrape \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "linkedin.com/jobs/view/123"}' \
  -v 2>&1 | grep "HTTP/"
```

**Résultat attendu:**
```
< HTTP/1.1 400 Bad Request
```

**Pas 422 !** 400 signifie que l'URL est acceptée mais le scraping échoue (car l'URL n'existe pas).

---

### Test 2: URL avec espaces (devrait être nettoyée)

```bash
curl -X POST http://localhost:8000/api/v1/job-offers/scrape \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "  linkedin.com/jobs/view/123  "}' \
  | jq
```

**Résultat:** Devrait fonctionner (espaces supprimés automatiquement)

---

### Test 3: URL complète (devrait toujours marcher)

```bash
curl -X POST http://localhost:8000/api/v1/job-offers/scrape \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.linkedin.com/jobs/view/123"}' \
  | jq
```

---

### Test 4: Plateforme non supportée

```bash
curl -X POST http://localhost:8000/api/v1/job-offers/scrape \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.monster.com/jobs/123"}' \
  | jq
```

**Résultat attendu:**
```json
{
  "detail": "Platform not supported. Supported platforms: LinkedIn, Indeed, Welcome to the Jungle."
}
```

---

## 📊 INTERPRÉTATION DES RÉSULTATS

| Code HTTP | Signification | Validation OK ? |
|-----------|--------------|-----------------|
| 200 | ✅ Scraping réussi | ✅ OUI |
| 400 "Platform not supported" | ⚠️ URL d'une plateforme non supportée | ✅ OUI (validation passe) |
| 400 "Failed to scrape..." | ⚠️ URL valide mais scraping échoue | ✅ OUI (validation passe) |
| 401 "Could not validate credentials" | ❌ Token invalide | ⬜ N/A (problème d'auth) |
| 422 Validation error | ❌ Format d'URL rejeté | ❌ NON (validation échoue) |

**Si vous obtenez 400 au lieu de 422, la correction fonctionne !** ✅

---

## 🔍 VÉRIFIER LES LOGS BACKEND

Dans le terminal où tourne `uvicorn`, vous devriez voir :

```
INFO:     Scraping request from user 1: https://linkedin.com/jobs/view/123
WARNING:  Scraping failed - platform not supported: Platform not supported...
```

ou

```
ERROR:    Scraping failed - error: Message: timeout...
```

**Si vous voyez ces logs, tout fonctionne correctement !**

---

## 🚀 SCRIPT COMPLET DE TEST

Copiez-collez ce script pour tout tester automatiquement :

```bash
#!/bin/bash

echo "======================================================================"
echo "🧪 TEST ENDPOINT /scrape - Validation URL Assouplie"
echo "======================================================================"
echo ""

# 1. Créer un compte (ignorer l'erreur si existe)
echo "📝 Création du compte de test..."
curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "scrape-test@example.com",
    "password": "test123",
    "name": "Scrape Test"
  }' > /dev/null 2>&1

# 2. Obtenir un token
echo "🔑 Obtention du token..."
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -F "username=scrape-test@example.com" \
  -F "password=test123" \
  | jq -r '.access_token')

if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
    echo "❌ Échec de l'authentification"
    exit 1
fi

echo "✅ Token obtenu: ${TOKEN:0:20}..."
echo ""

# 3. Test 1: URL sans https://
echo "======================================================================"
echo "TEST 1: URL sans https:// (devrait être acceptée)"
echo "======================================================================"
echo "URL: linkedin.com/jobs/view/123"
echo ""

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://localhost:8000/api/v1/job-offers/scrape \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "linkedin.com/jobs/view/123"}')

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

echo "Code HTTP: $HTTP_CODE"
echo "Réponse: $BODY" | jq '.' 2>/dev/null || echo "$BODY"
echo ""

if [ "$HTTP_CODE" = "422" ]; then
    echo "❌ ÉCHEC: Validation trop stricte (422)"
    echo "   Le serveur n'a peut-être pas été redémarré avec les modifications"
elif [ "$HTTP_CODE" = "400" ]; then
    echo "✅ SUCCÈS: URL acceptée (400 = scraping échoué, pas validation)"
elif [ "$HTTP_CODE" = "200" ]; then
    echo "✅ SUCCÈS: Scraping réussi !"
fi
echo ""

# 4. Test 2: URL avec espaces
echo "======================================================================"
echo "TEST 2: URL avec espaces (devrait être nettoyée)"
echo "======================================================================"
echo "URL: '  linkedin.com/jobs/view/123  '"
echo ""

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://localhost:8000/api/v1/job-offers/scrape \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "  linkedin.com/jobs/view/123  "}')

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)

echo "Code HTTP: $HTTP_CODE"

if [ "$HTTP_CODE" = "422" ]; then
    echo "❌ ÉCHEC: Espaces non nettoyés"
elif [ "$HTTP_CODE" = "400" ] || [ "$HTTP_CODE" = "200" ]; then
    echo "✅ SUCCÈS: URL nettoyée et acceptée"
fi
echo ""

# 5. Test 3: Plateforme non supportée
echo "======================================================================"
echo "TEST 3: Plateforme non supportée"
echo "======================================================================"
echo "URL: https://www.monster.com/jobs/123"
echo ""

RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/job-offers/scrape \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.monster.com/jobs/123"}')

echo "Réponse: $RESPONSE" | jq '.' 2>/dev/null || echo "$RESPONSE"

if echo "$RESPONSE" | grep -q "Platform not supported"; then
    echo "✅ SUCCÈS: Message d'erreur correct"
else
    echo "⚠️  Message d'erreur différent"
fi
echo ""

# Résumé
echo "======================================================================"
echo "📊 RÉSUMÉ"
echo "======================================================================"
echo "✅ La validation d'URL assouplie fonctionne si vous avez eu 400 au lieu de 422"
echo "✅ Le backend accepte maintenant les URLs avec ou sans https://"
echo "✅ Les espaces sont automatiquement supprimés"
echo ""
echo "📚 Pour tester avec une vraie URL LinkedIn:"
echo "   1. Trouvez une offre sur https://www.linkedin.com/jobs"
echo "   2. Copiez l'URL"
echo "   3. Lancez:"
echo ""
echo "   curl -X POST http://localhost:8000/api/v1/job-offers/scrape \\"
echo "     -H \"Authorization: Bearer \$TOKEN\" \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"url\": \"VOTRE_URL_ICI\"}' | jq"
echo ""
echo "======================================================================"
```

**Sauvegardez ce script dans `test_scrape.sh` et lancez:**

```bash
chmod +x test_scrape.sh
./test_scrape.sh
```

---

## 🎉 RÉSULTAT ATTENDU

Si tout fonctionne, vous devriez voir :

```
✅ SUCCÈS: URL acceptée (400 = scraping échoué, pas validation)
✅ SUCCÈS: URL nettoyée et acceptée
✅ SUCCÈS: Message d'erreur correct
```

**Cela prouve que la correction fonctionne !**

Le 400 est normal car les URLs de test n'existent pas. L'important c'est qu'elles soient **acceptées** (pas de 422).

---

## 📞 POUR LE FRONTEND

**Dites à l'équipe frontend:**

1. ✅ Le backend accepte maintenant les URLs avec ou sans `https://`
2. ✅ Ils peuvent tester directement sans modification de leur code
3. ✅ Si erreur 400, regarder `error.response?.data?.detail` pour le message exact
4. ⚠️ Pour tester, utiliser une **vraie URL LinkedIn** existante

**Exemple de vraie URL à tester:**
- https://www.linkedin.com/jobs/view/4079886035/
- https://www.indeed.fr/viewjob?jk=exemple
- https://www.welcometothejungle.com/fr/companies/company/jobs/job_id

---

**Les corrections sont actives. Le frontend peut tester !** 🚀
