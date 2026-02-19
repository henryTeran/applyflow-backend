# 🪟 ApplyFlow Backend - Guide Windows

## 🎯 Démarrage Ultra-Rapide (Windows)

### Méthode 1 : Double-clic (Plus simple)

1. **Double-cliquez sur** `start.bat`
2. Choisissez l'option 1 pour le setup initial (première fois seulement)
3. Ensuite, option 2 pour démarrer le serveur
4. Le navigateur s'ouvrira automatiquement sur http://localhost:8000/docs

### Méthode 2 : PowerShell (Plus d'options)

1. **Clic droit sur** `start.ps1` → "Exécuter avec PowerShell"
2. Suivez le menu interactif

### Méthode 3 : Ligne de commande

```powershell
# Ouvrir PowerShell dans ce dossier
.\start.ps1

# Ou directement :
wsl -e bash -c "cd /mnt/c/projets/ApplyFlow/backend && bash start.sh"
```

## 📋 Prérequis Windows

### 1. WSL2 (Windows Subsystem for Linux)

**Vérifier si WSL est installé :**

```powershell
wsl --version
```

**Si pas installé :**

```powershell
# Ouvrir PowerShell en Administrateur
wsl --install

# Redémarrer l'ordinateur
```

**Installer Ubuntu :**

```powershell
wsl --install -d Ubuntu-22.04
```

**Première configuration :**
- Créer un nom d'utilisateur
- Créer un mot de passe
- Retenir ces identifiants !

### 2. Conda dans WSL

**Ouvrir WSL :**

```powershell
wsl
```

**Dans WSL, installer Miniconda :**

```bash
cd ~
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
# Accepter les paramètres par défaut
source ~/.bashrc
```

**Vérifier :**

```bash
conda --version
# Devrait afficher : conda 23.x.x
```

## 🚀 Setup Initial (Première fois)

### Option A : Script automatique

```powershell
# Double-cliquer sur start.bat
# Choisir option 1 : Setup initial
```

### Option B : Manuel dans WSL

```powershell
# Ouvrir WSL
wsl

# Dans WSL :
cd /mnt/c/projets/ApplyFlow/backend
bash setup_wsl.sh
```

Le script va :
- ✅ Créer l'environnement conda `applyflow`
- ✅ Installer PostgreSQL
- ✅ Créer la base de données
- ✅ Configurer `.env`
- ✅ Lancer les migrations
- ✅ (Optionnel) Charger des données de test

## ▶️ Démarrer le Serveur

### Depuis Windows

```powershell
# Double-cliquer sur start.bat
# Choisir option 2 : Démarrer le serveur
```

### Depuis WSL

```bash
wsl
cd /mnt/c/projets/ApplyFlow/backend
./start.sh
```

### Vérifier que ça marche

Ouvrir dans le navigateur :
- 📚 **Documentation API** : http://localhost:8000/docs
- 🏥 **Health check** : http://localhost:8000/ping

## 📁 Structure des Fichiers Windows

```
c:\projets\ApplyFlow\backend\
│
├── start.bat              ← Double-cliquer ici (facile)
├── start.ps1              ← Ou ici (PowerShell)
│
├── setup_wsl.sh           ← Setup automatique WSL
├── start.sh               ← Démarrage serveur
├── environment.yml        ← Config Conda
│
├── GETTING_STARTED.md     ← Guide principal
├── START_HERE.md          ← Démarrage rapide
├── SETUP_WSL_CONDA.md     ← Guide détaillé WSL+Conda
└── README.md              ← Documentation complète
```

## 🎓 Utilisation Quotidienne

### Workflow typique

1. **Démarrer le serveur**
   ```powershell
   # Double-clic sur start.bat → Option 2
   ```

2. **Ouvrir VS Code** (optionnel)
   ```powershell
   code c:\projets\ApplyFlow\backend
   ```

3. **Utiliser l'API**
   - Naviguer vers http://localhost:8000/docs
   - Tester les endpoints interactivement

4. **Arrêter le serveur**
   - Appuyer sur `Ctrl+C` dans le terminal

### Commandes courantes

```powershell
# Charger des données de test
# start.bat → Option 3

# Lancer migrations
# start.bat → Option 5

# Ouvrir un terminal WSL dans le projet
# start.bat → Option 4
```

## 🔧 Configuration

### Éditer le fichier .env

```powershell
# Avec notepad
notepad c:\projets\ApplyFlow\backend\.env

# Ou avec VS Code
code c:\projets\ApplyFlow\backend\.env
```

### Paramètres importants

```env
# Base de données (déjà configuré par le setup)
DATABASE_URL=postgresql://applyflow_user:password@localhost:5432/applyflow_db

# Email (À CONFIGURER pour envoyer des emails)
SMTP_HOST=smtp.gmail.com
SMTP_USER=votre-email@gmail.com
SMTP_PASSWORD=votre-mot-de-passe-app

# OpenAI (optionnel)
OPENAI_API_KEY=sk-votre-clé
```

### Gmail : Créer un mot de passe d'application

1. Aller sur https://myaccount.google.com/apppasswords
2. Créer un mot de passe pour "ApplyFlow"
3. Copier le mot de passe dans `.env` → `SMTP_PASSWORD`

## 🧪 Tester l'Installation

### Depuis Windows (PowerShell)

```powershell
# Test 1 : Vérifier WSL
wsl echo "WSL fonctionne !"

# Test 2 : Vérifier Conda
wsl -e bash -c "conda --version"

# Test 3 : Vérifier PostgreSQL
wsl -e bash -c "sudo service postgresql status"

# Test 4 : Ping l'API (quand serveur lancé)
curl http://localhost:8000/ping
```

### Depuis le navigateur

Une fois le serveur lancé :

1. http://localhost:8000/ping → Devrait retourner `{"status":"ok","message":"pong"}`
2. http://localhost:8000/docs → Documentation interactive
3. http://localhost:8000/health → État du serveur

## 🐛 Dépannage Windows

### WSL ne démarre pas

```powershell
# Mettre à jour WSL
wsl --update

# Redémarrer WSL
wsl --shutdown
wsl
```

### Le serveur ne démarre pas

```powershell
# Vérifier les logs dans WSL
wsl
cd /mnt/c/projets/ApplyFlow/backend
./start.sh
# Regarder les messages d'erreur
```

### Port 8000 déjà utilisé

```powershell
# Trouver le processus
netstat -ano | findstr :8000

# Tuer le processus
taskkill /PID <numéro_PID> /F
```

### Problème de permissions

```powershell
# Dans WSL
wsl
sudo chown -R $USER:$USER /mnt/c/projets/ApplyFlow/backend
```

### Réinitialiser complètement

```powershell
# Dans WSL
wsl
cd /mnt/c/projets/ApplyFlow/backend

# Supprimer l'environnement conda
conda env remove -n applyflow

# Relancer le setup
bash setup_wsl.sh
```

## 💡 Astuces Windows

### Raccourci Bureau

Créer un raccourci vers `start.bat` sur le bureau :
1. Clic droit sur `start.bat`
2. "Créer un raccourci"
3. Déplacer sur le bureau

### Windows Terminal (Recommandé)

Installer Windows Terminal pour une meilleure expérience :

```powershell
winget install Microsoft.WindowsTerminal
```

Puis dans Windows Terminal :
- `Ctrl+Shift+P` → "Open Settings"
- Ajouter un profil pour ApplyFlow

### VS Code avec WSL

1. Installer l'extension "Remote - WSL" dans VS Code
2. Ouvrir VS Code : `code .`
3. Cliquer sur le coin inférieur gauche → "Reopen in WSL"

### Accès aux fichiers WSL depuis Windows

Dans l'Explorateur Windows, taper :
```
\\wsl$\Ubuntu-22.04\home\votre_nom\
```

## 📊 Workflow de Développement

### Développement Frontend/Backend séparé

Si vous développez aussi un frontend :

```powershell
# Terminal 1 : Backend (ce projet)
cd c:\projets\ApplyFlow\backend
.\start.ps1
# → Option 2

# Terminal 2 : Frontend (futur)
cd c:\projets\ApplyFlow\frontend
npm run dev
```

### Utiliser Postman/Insomnia

1. Importer la collection OpenAPI depuis http://localhost:8000/openapi.json
2. Tester les endpoints
3. Sauvegarder les requêtes courantes

### Base de données GUI

Installer un client PostgreSQL Windows pour voir la base :
- **pgAdmin** : https://www.pgadmin.org/
- **DBeaver** : https://dbeaver.io/

Connection :
- Host: `localhost`
- Port: `5432`
- Database: `applyflow_db`
- User: `applyflow_user`
- Password: (celui configuré pendant le setup)

## 🎯 Prochaines Étapes

1. ✅ **Setup complet** : `start.bat` → Option 1
2. ✅ **Charger des données de test** : `start.bat` → Option 3
3. ✅ **Démarrer le serveur** : `start.bat` → Option 2
4. ✅ **Tester l'API** : http://localhost:8000/docs
5. ✅ **Créer votre première offre d'emploi** dans l'API
6. ✅ **Lancer le pipeline** pour générer une candidature

## 📚 Documentation Complète

- **START_HERE.md** - Guide ultra-rapide
- **SETUP_WSL_CONDA.md** - Setup détaillé WSL+Conda
- **README.md** - Documentation technique complète
- **ARCHITECTURE.md** - Architecture du système
- **COMMANDS.md** - Référence des commandes

## 🎉 C'est Tout !

Votre environnement ApplyFlow est prêt sous Windows avec WSL + Conda !

**Besoin d'aide ?**
- Consultez [SETUP_WSL_CONDA.md](SETUP_WSL_CONDA.md) pour plus de détails
- Vérifiez [COMMANDS.md](COMMANDS.md) pour les commandes courantes

**Bon développement !** 🚀
