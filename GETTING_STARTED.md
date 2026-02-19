# ApplyFlow Backend - Guide de Démarrage

Choisissez votre méthode de setup préférée :

## 🐧 Option 1 : WSL + Conda (Recommandé pour Windows)

**Avantages :**
- ✅ Environnement Linux natif sur Windows
- ✅ Gestion simplifiée des dépendances avec Conda
- ✅ PostgreSQL dans WSL (performant)
- ✅ Scripts automatisés

**📖 Guide complet :** [SETUP_WSL_CONDA.md](docs/SETUP_WSL_CONDA.md)

**⚡ Démarrage rapide :** [START_HERE.md](START_HERE.md)

### Installation Express

```bash
# 1. Ouvrir WSL
wsl

# 2. Aller dans le projet
cd /mnt/c/projets/ApplyFlow/backend

# 3. Setup automatique
bash setup_wsl.sh

# 4. Démarrer
./start.sh
```

---

## 💻 Option 2 : Python Standard (Windows/Linux/Mac)

**Avantages :**
- ✅ Pas de WSL nécessaire
- ✅ Installation classique Python
- ✅ Compatible tous systèmes

**📖 Guide complet :** [README.md](README.md)

**⚡ Démarrage rapide :** [QUICKSTART.md](QUICKSTART.md)

### Installation Express

```bash
# 1. Créer environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 2. Installer dépendances
pip install -r requirements.txt

# 3. Configurer
cp .env.example .env
# Éditer .env avec vos paramètres

# 4. Setup base de données
createdb applyflow_db
python migrate.py

# 5. Démarrer
uvicorn app.main:app --reload
```

---

## 📚 Documentation Complète

| Fichier | Description |
|---------|-------------|
| **START_HERE.md** | 🚀 Démarrage ultra-rapide WSL+Conda (5 min) |
| **SETUP_WSL_CONDA.md** | 🐧 Guide détaillé WSL + Conda |
| **QUICKSTART.md** | ⚡ Guide de démarrage rapide général |
| **README.md** | 📖 Documentation complète du projet |
| **ARCHITECTURE.md** | 🏗️ Architecture et design patterns (dans `docs/`) |
| **COMMANDS.md** | 💻 Toutes les commandes utiles (dans `docs/`) |

---

## 🎯 Ce qui est inclus

### ✅ Backend complet et fonctionnel

- **6 modèles de données** : User, JobOffer, JobMatch, ApplicationDraft, Application, TimelineEvent
- **30+ endpoints REST** : CRUD complet pour toutes les entités
- **Matching intelligent** : Algorithme de scoring (0-100) avec justifications
- **Génération automatique** : Lettres de motivation + PDF + emails
- **Pipeline orchestré** : Tout en une seule commande
- **Base de données** : PostgreSQL avec migrations Alembic
- **Documentation** : OpenAPI/Swagger auto-générée

### 🛠️ Outils inclus

- `setup_wsl.sh` - Setup automatique WSL + Conda
- `start.sh` - Script de démarrage rapide
- `migrate.py` - Helper pour les migrations
- `seed_data.py` - Données de test (5 jobs + 1 user)
- `environment.yml` - Configuration Conda

---

## 🚀 Pour bien démarrer

### 1. Choisir votre méthode

- **Windows avec WSL** → [START_HERE.md](START_HERE.md)
- **Autre système** → [QUICKSTART.md](QUICKSTART.md)

### 2. Suivre le guide

Chaque guide vous explique pas à pas comment :
- Installer les prérequis
- Configurer l'environnement
- Créer la base de données
- Démarrer le serveur
- Tester l'API

### 3. Explorer l'API

Une fois le serveur lancé :
- **Documentation interactive** : http://localhost:8000/docs
- **Alternative ReDoc** : http://localhost:8000/redoc
- **Endpoint de test** : http://localhost:8000/ping

---

## 📞 Besoin d'aide ?

### Vous utilisez WSL + Conda ?
→ Consultez [SETUP_WSL_CONDA.md](docs/SETUP_WSL_CONDA.md)

### Vous utilisez Python standard ?
→ Consultez [README.md](README.md)

### Vous voulez comprendre l'architecture ?
→ Consultez [ARCHITECTURE.md](docs/ARCHITECTURE.md)

### Vous cherchez une commande spécifique ?
→ Consultez [COMMANDS.md](docs/COMMANDS.md)

---

## 🎯 Prochaines étapes

Une fois le serveur lancé :

1. **Tester l'API** sur http://localhost:8000/docs
2. **Charger des données de test** : `python seed_data.py`
3. **Créer une offre d'emploi** via POST `/api/v1/job-offers/`
4. **Lancer le pipeline** via POST `/api/v1/job-offers/{id}/run-pipeline`
5. **Consulter les résultats** dans les endpoints `/job-matches/` et `/drafts/`

---

## ⭐ Recommandation

Pour Windows, nous recommandons **WSL + Conda** :
- Environnement Linux performant
- Setup automatisé avec `setup_wsl.sh`
- Scripts de démarrage pratiques
- Meilleure compatibilité pour les dépendances

📖 **Commencer ici :** [START_HERE.md](START_HERE.md)

---

Bon développement ! 🚀
