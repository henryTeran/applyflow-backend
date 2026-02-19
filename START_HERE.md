# 🎯 ApplyFlow - Setup Rapide WSL + Conda

## ⚡ Installation Express (5 minutes)

### 1️⃣ Ouvrir WSL

```powershell
# Depuis PowerShell Windows
wsl
```

### 2️⃣ Aller dans le projet

```bash
cd /mnt/c/projets/ApplyFlow/backend
```

### 3️⃣ Lancer le setup automatique

```bash
bash setup_wsl.sh
```

Le script va automatiquement :
- ✅ Créer l'environnement conda `applyflow`
- ✅ Installer PostgreSQL (si nécessaire)
- ✅ Créer la base de données
- ✅ Configurer le fichier `.env`
- ✅ Lancer les migrations
- ✅ Charger des données de test (optionnel)

### 4️⃣ Démarrer le serveur

```bash
./start.sh
```

### 5️⃣ Ouvrir la documentation

🌐 http://localhost:8000/docs

## 🚀 Démarrage Quotidien

```bash
# Ouvrir WSL
wsl

# Aller dans le projet
cd /mnt/c/projets/ApplyFlow/backend

# Démarrer (tout est automatique)
./start.sh
```

Le script `start.sh` :
- Démarre PostgreSQL
- Active l'environnement conda
- Lance le serveur FastAPI

## 📋 Commandes Utiles

### Gestion de l'environnement Conda

```bash
# Activer l'environnement
conda activate applyflow

# Désactiver
conda deactivate

# Lister les environnements
conda env list

# Mettre à jour les packages
conda update --all
```

### Gestion de PostgreSQL

```bash
# Démarrer
sudo service postgresql start

# Statut
sudo service postgresql status

# Se connecter à la base
psql -U applyflow_user -d applyflow_db
```

### Migrations de base de données

```bash
# Créer une migration
alembic revision --autogenerate -m "Description"

# Appliquer les migrations
alembic upgrade head

# Voir l'historique
alembic history
```

### Tests et développement

```bash
# Charger des données de test
python seed_data.py

# Accéder à un shell Python avec les models
python
>>> from app.database import SessionLocal
>>> from app.models import JobOffer
>>> db = SessionLocal()
>>> jobs = db.query(JobOffer).all()
```

## 🛠️ Configuration

### Modifier le profil candidat

Éditer `app/services/match_service.py` :

```python
DEFAULT_CANDIDATE = CandidateProfile(
    name="Votre Nom",
    title="Votre Titre",
    years_of_experience=5,
    technical_skills=["Python", "FastAPI", ...],
    # ... personnaliser tous les champs
)
```

### Modifier le template de lettre

Éditer `app/templates/cover_letter_base.html`

### Configurer SMTP pour l'envoi d'emails

Éditer `.env` :

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=votre-email@gmail.com
SMTP_PASSWORD=votre-mot-de-passe-app
```

Pour Gmail : Créer un mot de passe d'application sur https://myaccount.google.com/apppasswords

## 📚 Documentation Complète

- **SETUP_WSL_CONDA.md** - Guide détaillé WSL + Conda
- **README.md** - Documentation complète du projet
- **QUICKSTART.md** - Guide de démarrage rapide
- **ARCHITECTURE.md** - Architecture du système
- **COMMANDS.md** - Toutes les commandes

## 🎯 Workflow Typique

### 1. Ajouter une offre d'emploi

```bash
curl -X POST http://localhost:8000/api/v1/job-offers/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Python Developer",
    "company": "TechCorp",
    "location": "Genève",
    "source": "LinkedIn",
    "application_type": "email",
    "raw_description": "Description du poste..."
  }'
```

### 2. Lancer le pipeline complet

```bash
curl -X POST http://localhost:8000/api/v1/job-offers/1/run-pipeline
```

Cela va :
- Calculer le score de matching
- Générer la lettre de motivation
- Créer le PDF
- Préparer l'email

### 3. Consulter les résultats

🌐 http://localhost:8000/docs

Ou via curl :

```bash
# Voir les matches
curl http://localhost:8000/api/v1/job-matches/

# Voir les drafts
curl http://localhost:8000/api/v1/drafts/
```

### 4. Enregistrer la candidature

Après avoir envoyé manuellement :

```bash
curl -X POST http://localhost:8000/api/v1/applications/ \
  -H "Content-Type: application/json" \
  -d '{
    "job_offer_id": 1,
    "channel": "email",
    "submitted_by": "manual",
    "status": "sent",
    "sent_at": "2025-12-01T10:00:00Z"
  }'
```

## 🐛 Dépannage

### Le serveur ne démarre pas

```bash
# Vérifier que PostgreSQL est lancé
sudo service postgresql status

# Vérifier que l'environnement conda est activé
conda activate applyflow

# Vérifier la connexion à la base
psql -U applyflow_user -d applyflow_db
```

### Erreurs de migration

```bash
# Réinitialiser les migrations
rm alembic/versions/*.py
python migrate.py
```

### Port 8000 déjà utilisé

```bash
# Trouver le processus
sudo lsof -i :8000

# Le tuer
sudo kill -9 <PID>

# Ou utiliser un autre port
uvicorn app.main:app --reload --port 8080
```

## 💡 Astuces

### Ouvrir VS Code dans WSL

```bash
# Depuis WSL
code /mnt/c/projets/ApplyFlow/backend
```

### Auto-démarrage PostgreSQL

Ajouter à `~/.bashrc` :

```bash
sudo service postgresql start
```

### Alias pratiques

Ajouter à `~/.bashrc` :

```bash
alias applyflow='cd /mnt/c/projets/ApplyFlow/backend && conda activate applyflow'
alias afs='cd /mnt/c/projets/ApplyFlow/backend && ./start.sh'
```

Puis :

```bash
source ~/.bashrc
afs  # Lance directement le serveur !
```

## 🎉 C'est tout !

Votre backend ApplyFlow est prêt à l'emploi avec WSL + Conda.

**Prochaines étapes :**
1. ✅ Tester l'API sur http://localhost:8000/docs
2. ✅ Personnaliser votre profil candidat
3. ✅ Ajouter vos vraies offres d'emploi
4. ✅ Profiter du système !

**Besoin d'aide ?** Consultez SETUP_WSL_CONDA.md pour plus de détails.
