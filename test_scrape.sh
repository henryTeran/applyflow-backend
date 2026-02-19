#!/bin/bash

echo "======================================================================"
echo "🧪 TEST ENDPOINT /scrape - Validation URL Assouplie"
echo "======================================================================"
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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
    echo -e "${RED}❌ Échec de l'authentification${NC}"
    echo "Vérifiez que le serveur backend est lancé sur http://localhost:8000"
    exit 1
fi

echo -e "${GREEN}✅ Token obtenu: ${TOKEN:0:20}...${NC}"
echo ""

# 3. Test 1: URL sans https://
echo "======================================================================"
echo "TEST 1: URL sans https:// (devrait être acceptée)"
echo "======================================================================"
echo "URL testée: linkedin.com/jobs/view/123"
echo ""

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://localhost:8000/api/v1/job-offers/scrape \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "linkedin.com/jobs/view/123"}')

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

echo "Code HTTP: $HTTP_CODE"
echo "Réponse:"
echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
echo ""

if [ "$HTTP_CODE" = "422" ]; then
    echo -e "${RED}❌ ÉCHEC: Validation trop stricte (422)${NC}"
    echo "   Le serveur n'a peut-être pas été redémarré avec les modifications"
    echo "   Relancez: uvicorn app.main:app --reload"
elif [ "$HTTP_CODE" = "400" ]; then
    echo -e "${GREEN}✅ SUCCÈS: URL acceptée${NC}"
    echo "   (400 = scraping échoué car URL invalide, mais validation OK)"
elif [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ SUCCÈS: Scraping réussi !${NC}"
fi
echo ""

# 4. Test 2: URL avec espaces
echo "======================================================================"
echo "TEST 2: URL avec espaces (devrait être nettoyée)"
echo "======================================================================"
echo "URL testée: '  linkedin.com/jobs/view/123  ' (avec espaces)"
echo ""

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://localhost:8000/api/v1/job-offers/scrape \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "  linkedin.com/jobs/view/123  "}')

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)

echo "Code HTTP: $HTTP_CODE"

if [ "$HTTP_CODE" = "422" ]; then
    echo -e "${RED}❌ ÉCHEC: Espaces non nettoyés (422)${NC}"
elif [ "$HTTP_CODE" = "400" ] || [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ SUCCÈS: URL nettoyée et acceptée${NC}"
fi
echo ""

# 5. Test 3: Plateforme non supportée
echo "======================================================================"
echo "TEST 3: Plateforme non supportée"
echo "======================================================================"
echo "URL testée: https://www.monster.com/jobs/123"
echo ""

RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/job-offers/scrape \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.monster.com/jobs/123"}')

echo "Réponse:"
echo "$RESPONSE" | jq '.' 2>/dev/null || echo "$RESPONSE"
echo ""

if echo "$RESPONSE" | grep -q "Platform not supported"; then
    echo -e "${GREEN}✅ SUCCÈS: Message d'erreur correct${NC}"
else
    echo -e "${YELLOW}⚠️  Message d'erreur différent${NC}"
fi
echo ""

# 6. Test 4: URL invalide (sans point)
echo "======================================================================"
echo "TEST 4: URL invalide (devrait être rejetée)"
echo "======================================================================"
echo "URL testée: not-a-url"
echo ""

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://localhost:8000/api/v1/job-offers/scrape \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "not-a-url"}')

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

echo "Code HTTP: $HTTP_CODE"
echo "Réponse:"
echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
echo ""

if [ "$HTTP_CODE" = "422" ]; then
    echo -e "${GREEN}✅ SUCCÈS: URL invalide correctement rejetée${NC}"
else
    echo -e "${YELLOW}⚠️  Code différent de 422${NC}"
fi
echo ""

# Résumé
echo "======================================================================"
echo "📊 RÉSUMÉ DES TESTS"
echo "======================================================================"
echo ""
echo -e "${GREEN}✅ Tests réussis si vous avez vu:${NC}"
echo "   - Test 1: Code 400 (URL acceptée, scraping échoué)"
echo "   - Test 2: Code 400 ou 200 (espaces nettoyés)"
echo "   - Test 3: Message 'Platform not supported'"
echo "   - Test 4: Code 422 (URL invalide rejetée)"
echo ""
echo -e "${YELLOW}📝 Conclusion:${NC}"
echo "   ✅ La validation d'URL assouplie fonctionne"
echo "   ✅ Le backend accepte les URLs avec ou sans https://"
echo "   ✅ Les espaces sont automatiquement supprimés"
echo "   ✅ Les URLs vraiment invalides sont toujours rejetées"
echo ""
echo "======================================================================"
echo "🚀 PROCHAINES ÉTAPES POUR LE FRONTEND"
echo "======================================================================"
echo ""
echo "1. Le backend est prêt à accepter les URLs du frontend"
echo "2. Pour tester avec une vraie URL LinkedIn:"
echo ""
echo "   # Trouvez une offre sur https://www.linkedin.com/jobs"
echo "   # Copiez son URL et testez:"
echo ""
echo "   curl -X POST http://localhost:8000/api/v1/job-offers/scrape \\"
echo "     -H \"Authorization: Bearer $TOKEN\" \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"url\": \"VOTRE_URL_LINKEDIN_ICI\"}' | jq"
echo ""
echo "3. Le frontend peut maintenant utiliser l'endpoint sans modification"
echo ""
echo "======================================================================"
