# 🔧 Installation Selenium - Guide Rapide

## Installation des Dépendances

### 1. Installer les packages Python

```bash
cd /mnt/c/projets/ApplyFlow/backend
pip install selenium==4.16.0 webdriver-manager==4.0.1
```

### 2. Vérifier l'installation

```bash
python -c "from selenium import webdriver; print('✅ Selenium installé')"
python -c "from webdriver_manager.chrome import ChromeDriverManager; print('✅ WebDriver Manager installé')"
```

---

## Configuration ChromeDriver

### Windows/WSL (Automatique)
```bash
# Le ChromeDriver sera téléchargé automatiquement au premier lancement
# Rien à faire !
```

### Linux (Manuel si nécessaire)
```bash
# Si l'installation automatique échoue
sudo apt-get update
sudo apt-get install -y chromium-browser chromium-chromedriver

# Ou installer Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f
```

### Docker (Ajouter au Dockerfile)
```dockerfile
# Ajouter ces lignes au Dockerfile
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    chromium \
    chromium-driver

# Définir les variables d'environnement
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER=/usr/bin/chromedriver
```

---

## Test du Scraping

### Test 1: Vérifier que Selenium fonctionne

```bash
# Créer un script de test
cat > test_selenium.py << 'EOF'
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

try:
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.google.com")
    print(f"✅ Page title: {driver.title}")
    driver.quit()
    print("✅ Selenium fonctionne parfaitement !")
except Exception as e:
    print(f"❌ Erreur: {e}")
EOF

python test_selenium.py
```

### Test 2: Tester le scraping service

```bash
# Créer un test du service
cat > test_scraping.py << 'EOF'
from app.services.scraping_service import scrape_job_offer

# Test LinkedIn
try:
    result = scrape_job_offer("https://www.linkedin.com/jobs/view/3787654321/")
    print(f"✅ LinkedIn scraping OK")
    print(f"   Title: {result.title}")
    print(f"   Company: {result.company}")
except Exception as e:
    print(f"❌ LinkedIn error: {e}")

# Test Indeed
try:
    result = scrape_job_offer("https://www.indeed.com/viewjob?jk=123456")
    print(f"✅ Indeed scraping OK")
except Exception as e:
    print(f"⚠️  Indeed error (peut être normal si URL invalide): {e}")

print("\n✅ Service de scraping configuré !")
EOF

python test_scraping.py
```

### Test 3: Tester l'endpoint API

```bash
# Démarrer le serveur
uvicorn app.main:app --reload --port 8000 &

# Attendre le démarrage
sleep 5

# Se connecter
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -F "username=test@example.com" \
  -F "password=test123" \
  | jq -r '.access_token')

# Tester le scraping
curl -X POST http://localhost:8000/api/v1/job-offers/scrape \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.linkedin.com/jobs/view/3787654321/"
  }' | jq

# Si ça fonctionne, vous verrez :
# {
#   "title": "...",
#   "company": "...",
#   "location": "...",
#   "description": "...",
#   "application_type": "portal",
#   "application_url": "https://..."
# }
```

---

## Résolution des Problèmes

### Erreur: "ChromeDriver not found"

**Solution 1: Laisser webdriver-manager l'installer**
```python
# Le code fait déjà ceci automatiquement:
from webdriver_manager.chrome import ChromeDriverManager
driver = webdriver.Chrome(ChromeDriverManager().install())
```

**Solution 2: Installation manuelle**
```bash
# Télécharger ChromeDriver
wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE
VERSION=$(cat LATEST_RELEASE)
wget https://chromedriver.storage.googleapis.com/$VERSION/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
```

### Erreur: "Chrome binary not found"

**Windows/WSL:**
```bash
# Installer Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
```

**Linux:**
```bash
sudo apt-get install chromium-browser
```

### Erreur: "Session not created"

**Vérifier les options:**
```python
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')  # Ajouter si nécessaire
```

### Erreur: "TimeoutException"

**Augmenter le timeout:**
```python
# Dans scraping_service.py
wait = WebDriverWait(driver, 15)  # Au lieu de 10
```

### LinkedIn bloque le scraping

**Solutions:**
1. Ajouter un User-Agent réaliste (déjà fait)
2. Ajouter des cookies (si nécessaire)
3. Utiliser un proxy (pour gros volume)
4. Alternative: API externe (ScrapingBee, etc.)

---

## Optimisations

### 1. Pool de Drivers (pour performances)

```python
# Créer un pool de drivers réutilisables
from queue import Queue

driver_pool = Queue(maxsize=5)

def get_driver_from_pool():
    if driver_pool.empty():
        return get_chrome_driver()
    return driver_pool.get()

def return_driver_to_pool(driver):
    driver_pool.put(driver)
```

### 2. Cache des Résultats

```python
# Utiliser Redis pour cacher les résultats
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def scrape_with_cache(url: str):
    # Vérifier cache
    cached = redis_client.get(f"scrape:{url}")
    if cached:
        return ScrapeResult(**json.loads(cached))
    
    # Scraper
    result = scrape_job_offer(url)
    
    # Mettre en cache (24h)
    redis_client.setex(f"scrape:{url}", 86400, result.json())
    
    return result
```

### 3. Rate Limiting

```python
# Limiter à 10 scrapes par minute par utilisateur
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/scrape")
@limiter.limit("10/minute")
async def scrape_job_posting(...):
    ...
```

---

## Monitoring

### Logs de Scraping

```bash
# Les logs sont dans app/services/scraping_service.py
# Pour voir les logs en temps réel:

tail -f logs/applyflow.log | grep -i scraping
```

### Métriques

```python
# Ajouter des métriques (optionnel)
import time

scraping_times = []

def scrape_with_metrics(url: str):
    start = time.time()
    try:
        result = scrape_job_offer(url)
        duration = time.time() - start
        scraping_times.append(duration)
        logger.info(f"Scraping took {duration:.2f}s")
        return result
    except Exception as e:
        logger.error(f"Scraping failed after {time.time() - start:.2f}s")
        raise
```

---

## Checklist Finale

- [ ] `pip install selenium webdriver-manager` exécuté
- [ ] Test Selenium basique réussi (`test_selenium.py`)
- [ ] Test scraping service réussi (`test_scraping.py`)
- [ ] Endpoint API `/scrape` testé avec cURL
- [ ] LinkedIn scraping fonctionne
- [ ] Indeed scraping fonctionne (optionnel)
- [ ] WTTJ scraping fonctionne (optionnel)
- [ ] Logs de scraping visibles
- [ ] Pas d'erreurs ChromeDriver

---

## Support

**Si problèmes persistants:**
1. Vérifier les logs : `tail -f logs/applyflow.log`
2. Tester Selenium en isolation : `python test_selenium.py`
3. Vérifier Chrome installé : `google-chrome --version`
4. Vérifier ChromeDriver : `chromedriver --version`

**Alternative rapide (développement uniquement):**
Créer un endpoint mock temporaire qui retourne des données factices, le remplacer par le vrai scraping plus tard.

---

**Selenium prêt ? → Tester la Candidature Express ! 🚀**
