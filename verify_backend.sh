#!/bin/bash
# Script de vérification finale du backend ApplyFlow
# À lancer avant déploiement en production

set -e

echo "======================================"
echo "  VÉRIFICATION BACKEND APPLYFLOW"
echo "======================================"
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0

check_pass() {
    echo -e "${GREEN}✅ $1${NC}"
    ((PASSED++))
}

check_fail() {
    echo -e "${RED}❌ $1${NC}"
    ((FAILED++))
}

check_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 1. Vérifier que conda env existe
echo "1️⃣  Vérification environnement Conda..."
if conda env list | grep -q "applyflow"; then
    check_pass "Environnement conda 'applyflow' trouvé"
else
    check_fail "Environnement conda 'applyflow' manquant"
fi
echo ""

# 2. Vérifier fichiers critiques
echo "2️⃣  Vérification fichiers critiques..."
if [ -f ".env" ]; then
    check_pass "Fichier .env existe"
else
    check_fail "Fichier .env manquant"
fi

if [ -f "requirements.txt" ]; then
    check_pass "requirements.txt existe"
else
    check_fail "requirements.txt manquant"
fi

if [ -f "alembic.ini" ]; then
    check_pass "alembic.ini existe"
else
    check_fail "alembic.ini manquant"
fi
echo ""

# 3. Vérifier .env sécurisé
echo "3️⃣  Vérification sécurité .env..."
if grep -q "changez-cette-cle-secrete" .env 2>/dev/null; then
    check_fail "SECRET_KEY par défaut détecté - CHANGER!"
else
    check_pass "SECRET_KEY personnalisé"
fi

if grep -q 'allow_origins=\["\*"\]' app/main.py 2>/dev/null; then
    check_fail "CORS wildcard détecté - À RESTREINDRE!"
else
    check_pass "CORS restreint"
fi
echo ""

# 4. Vérifier structure app/
echo "4️⃣  Vérification structure du code..."
if [ -d "app/api/v1" ]; then
    check_pass "Structure API v1 présente"
else
    check_fail "Structure API v1 manquante"
fi

if [ -f "app/api/v1/health.py" ]; then
    check_pass "Health checks implémentés"
else
    check_fail "Health checks manquants"
fi

if [ -d "app/models" ] && [ -d "app/schemas" ] && [ -d "app/crud" ]; then
    check_pass "Architecture MVC présente"
else
    check_fail "Architecture MVC incomplète"
fi
echo ""

# 5. Vérifier tests
echo "5️⃣  Vérification tests..."
if [ -d "tests" ]; then
    check_pass "Dossier tests/ existe"
    
    if [ -f "pytest.ini" ]; then
        check_pass "pytest.ini configuré"
    else
        check_warn "pytest.ini manquant"
    fi
else
    check_fail "Dossier tests/ manquant"
fi
echo ""

# 6. Vérifier dépendances Python
echo "6️⃣  Vérification dépendances Python..."
if python -c "import fastapi" 2>/dev/null; then
    check_pass "FastAPI installé"
else
    check_fail "FastAPI manquant - run: pip install -r requirements.txt"
fi

if python -c "import sqlalchemy" 2>/dev/null; then
    check_pass "SQLAlchemy installé"
else
    check_fail "SQLAlchemy manquant"
fi

if python -c "import structlog" 2>/dev/null; then
    check_pass "structlog installé"
else
    check_fail "structlog manquant"
fi
echo ""

# 7. Vérifier PostgreSQL
echo "7️⃣  Vérification PostgreSQL..."
if command -v psql &> /dev/null; then
    check_pass "PostgreSQL client installé"
    
    if pg_isready -q 2>/dev/null; then
        check_pass "PostgreSQL server en cours d'exécution"
    else
        check_warn "PostgreSQL server arrêté"
    fi
else
    check_fail "PostgreSQL client manquant"
fi
echo ""

# 8. Vérifier Redis
echo "8️⃣  Vérification Redis..."
if command -v redis-cli &> /dev/null; then
    check_pass "Redis client installé"
    
    if redis-cli ping 2>/dev/null | grep -q "PONG"; then
        check_pass "Redis server en cours d'exécution"
    else
        check_warn "Redis server arrêté"
    fi
else
    check_fail "Redis client manquant"
fi
echo ""

# 9. Lancer tests si possible
echo "9️⃣  Lancement tests automatisés..."
if command -v pytest &> /dev/null; then
    if pytest tests/ -v --tb=short 2>&1 | grep -q "passed"; then
        check_pass "Tests unitaires passent"
    else
        check_fail "Tests unitaires échouent"
    fi
else
    check_warn "pytest non installé - impossible de lancer les tests"
fi
echo ""

# 10. Vérifier documentation
echo "🔟 Vérification documentation..."
DOCS=(README.md AUDIT_PRODUCTION.md FINALISATION.md GUIDE_TESTS.md)
for doc in "${DOCS[@]}"; do
    if [ -f "$doc" ]; then
        check_pass "$doc présent"
    else
        check_warn "$doc manquant"
    fi
done
echo ""

# Résumé
echo "======================================"
echo "  RÉSUMÉ"
echo "======================================"
echo -e "${GREEN}✅ Tests réussis: $PASSED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}❌ Tests échoués: $FAILED${NC}"
else
    echo -e "${GREEN}❌ Tests échoués: 0${NC}"
fi
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 Backend ApplyFlow est prêt pour la production!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Corriger les erreurs avant déploiement${NC}"
    exit 1
fi
