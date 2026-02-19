# 🧪 GUIDE DE TEST DU BACKEND APPLYFLOW

## ✅ Prérequis
Assurez-vous que les services sont démarrés :
```bash
sudo service postgresql start
sudo service redis-server start
bash start.sh
```

Le serveur doit être accessible sur : http://localhost:8000

---

## 📋 TESTS MANUELS PAS À PAS

### ÉTAPE 1 : Test de l'API de base 🏠

Ouvrez votre navigateur sur : http://localhost:8000

Vous devriez voir :
```json
{
  "message": "Welcome to ApplyFlow API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

✅ **Test réussi** si vous voyez ce message JSON

---

### ÉTAPE 2 : Documentation Swagger 📚

Allez sur : http://localhost:8000/docs

Vous verrez l'interface Swagger UI avec toutes les routes disponibles :
- 🔐 **auth** - Authentification
- 👤 **users** - Gestion des utilisateurs
- 💼 **job-offers** - Offres d'emploi  
- 📝 **drafts** - Brouillons de candidature
- 📤 **applications** - Candidatures
- 📊 **timeline** - Historique d'activités

✅ **Test réussi** si l'interface Swagger s'affiche correctement

---

### ÉTAPE 3 : Créer un utilisateur 👤

Dans Swagger (http://localhost:8000/docs), trouvez la section **users** :

1. Cliquez sur `POST /api/v1/users/register`
2. Cliquez sur **Try it out**
3. Remplissez avec ces données :
```json
{
  "email": "jean.dupont@example.com",
  "password": "MonMotDePasse123!",
  "full_name": "Jean Dupont"
}
```
4. Cliquez sur **Execute**

**Résultat attendu :**
- Code 200
- Réponse contenant l'utilisateur créé avec son ID

✅ **Test réussi** si vous obtenez un code 200 et un objet utilisateur

---

### ÉTAPE 4 : Se connecter 🔐

Dans la section **auth** :

1. Cliquez sur `POST /api/v1/auth/login`
2. Cliquez sur **Try it out**
3. Remplissez les champs :
   - **username** : jean.dupont@example.com
   - **password** : MonMotDePasse123!
4. Cliquez sur **Execute**

**Résultat attendu :**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhb...",
  "token_type": "bearer"
}
```

**IMPORTANT :** Copiez le `access_token`, vous en aurez besoin !

Pour l'utiliser dans Swagger :
1. Cliquez sur le bouton 🔓 **Authorize** en haut de la page
2. Entrez : `Bearer VOTRE_TOKEN_ICI`
3. Cliquez sur **Authorize**

✅ **Test réussi** si vous obtenez un token JWT

---

### ÉTAPE 5 : Créer une offre d'emploi 💼

Dans la section **job-offers** :

1. Cliquez sur `POST /api/v1/job-offers/`
2. Cliquez sur **Try it out**
3. Remplissez avec :
```json
{
  "title": "Développeur Full Stack Python",
  "company": "TechCorp Solutions",
  "location": "Paris, France",
  "job_type": "CDI",
  "description": "Nous recherchons un développeur Python/FastAPI expérimenté pour rejoindre notre équipe dynamique.",
  "requirements": "- 3+ ans d'expérience Python\n- Connaissance de FastAPI\n- PostgreSQL",
  "salary_range": "45k-65k EUR",
  "url": "https://example.com/job/12345",
  "user_id": 1
}
```
4. Cliquez sur **Execute**

✅ **Test réussi** si code 200 et l'offre est créée

---

### ÉTAPE 6 : Lister les offres d'emploi 📋

1. Cliquez sur `GET /api/v1/job-offers/`
2. Cliquez sur **Try it out**
3. Cliquez sur **Execute**

**Résultat attendu :**
- Liste des offres d'emploi créées
- Vous devriez voir l'offre créée à l'étape 5

✅ **Test réussi** si vous voyez au moins une offre

---

### ÉTAPE 7 : Créer un brouillon de candidature ✏️

Dans la section **drafts** :

1. Cliquez sur `POST /api/v1/drafts/`
2. Remplissez avec :
```json
{
  "job_offer_id": 1,
  "user_id": 1,
  "cover_letter": "Madame, Monsieur,\n\nJe suis très intéressé par le poste de Développeur Full Stack...",
  "custom_resume": "CV personnalisé pour ce poste"
}
```
3. Cliquez sur **Execute**

✅ **Test réussi** si le brouillon est créé (code 200)

---

### ÉTAPE 8 : Créer une candidature 📤

Dans la section **applications** :

1. Cliquez sur `POST /api/v1/applications/`
2. Remplissez avec :
```json
{
  "job_offer_id": 1,
  "user_id": 1,
  "cover_letter": "Madame, Monsieur,\n\nJe vous écris pour postuler au poste de Développeur Full Stack Python...",
  "resume_url": "https://mon-cv.com/cv.pdf",
  "status": "submitted"
}
```
3. Cliquez sur **Execute**

**Statuts possibles :**
- `draft` - Brouillon
- `submitted` - Soumise
- `reviewing` - En cours de révision
- `interview` - Entretien
- `rejected` - Rejetée
- `accepted` - Acceptée

✅ **Test réussi** si la candidature est créée

---

### ÉTAPE 9 : Consulter son profil 👨‍💼

1. Cliquez sur `GET /api/v1/users/me`
2. Cliquez sur **Try it out**
3. Cliquez sur **Execute**

**Résultat attendu :**
- Vos informations de profil
- Email, nom complet, etc.

✅ **Test réussi** si vous voyez vos informations

---

### ÉTAPE 10 : Consulter la timeline 📊

Dans la section **timeline** :

1. Cliquez sur `GET /api/v1/timeline/user/{user_id}`
2. Entrez `1` comme user_id
3. Cliquez sur **Execute**

**Résultat attendu :**
- Liste des événements (création d'offre, candidature, etc.)
- Chaque événement avec sa date et description

✅ **Test réussi** si vous voyez l'historique d'activités

---

## 🚀 TEST AUTOMATISÉ

Pour un test automatique complet, exécutez :

```bash
python test_backend.py
```

Ce script teste automatiquement :
- ✅ Connexion API
- ✅ Création utilisateur
- ✅ Authentification
- ✅ Création offre d'emploi
- ✅ Gestion des brouillons
- ✅ Création de candidatures
- ✅ Récupération du profil
- ✅ Timeline d'activités

---

## 📊 VÉRIFIER LA BASE DE DONNÉES

Pour voir les données dans PostgreSQL :

```bash
sudo -u postgres psql -d applyflow -c "SELECT * FROM users;"
sudo -u postgres psql -d applyflow -c "SELECT * FROM job_offers;"
sudo -u postgres psql -d applyflow -c "SELECT * FROM applications;"
```

---

## ❌ RÉSOLUTION DE PROBLÈMES

### Erreur 500 - Internal Server Error
```bash
# Vérifier les logs du serveur
# Redémarrer PostgreSQL
sudo service postgresql restart

# Redémarrer Redis
sudo service redis-server restart
```

### Erreur de connexion
```bash
# Vérifier que le serveur est démarré
curl http://localhost:8000/

# Si pas de réponse, relancer le serveur
bash start.sh
```

### Erreur d'authentification
- Vérifiez que vous avez copié le token correctement
- Le token doit commencer par "Bearer " dans Swagger
- Reconnectez-vous si le token a expiré (30 min par défaut)

---

## ✨ FONCTIONNALITÉS À TESTER

- [x] Création de compte
- [x] Connexion/Déconnexion
- [x] Gestion des offres d'emploi
- [x] Création de brouillons
- [x] Soumission de candidatures
- [x] Suivi de l'état des candidatures
- [x] Timeline d'activités
- [x] Upload de fichiers (CV)
- [x] Matching automatique
- [x] Génération de lettres de motivation (AI)

---

## 📝 NOTES

- Tous les mots de passe sont hashés avec bcrypt
- Les tokens JWT expirent après 30 minutes
- La base de données utilise PostgreSQL
- Redis est utilisé pour le rate limiting
- Les fichiers uploadés sont stockés dans `/uploads`

---

## 🎉 SUCCÈS !

Si tous les tests passent, votre backend ApplyFlow est **100% fonctionnel** ! 🚀
