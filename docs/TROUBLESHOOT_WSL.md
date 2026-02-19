# 🔧 Résolution des problèmes VS Code WSL

## Problème : VS Code ne se connecte pas à WSL

### Solution rapide (Automatique)

**Double-cliquez sur :** `fix_vscode_wsl.bat`

Ou dans PowerShell :
```powershell
.\fix_vscode_wsl.ps1
```

---

### Solution manuelle

#### 1️⃣ Vérifier que WSL fonctionne

```powershell
wsl --list --verbose
# Ubuntu doit être "Running"
```

Si "Stopped" :
```powershell
wsl
```

#### 2️⃣ Redémarrer WSL

```powershell
wsl --shutdown
wsl
```

#### 3️⃣ Nettoyer le cache VS Code WSL

```powershell
wsl rm -rf ~/.vscode-server
```

#### 4️⃣ Réinstaller l'extension Remote-WSL

Dans VS Code :
1. `Ctrl+Shift+X` pour ouvrir les extensions
2. Rechercher "Remote - WSL"
3. Cliquer sur le bouton **⚙️** → **Désinstaller**
4. Fermer VS Code complètement
5. Rouvrir VS Code
6. Réinstaller "Remote - WSL"

#### 5️⃣ Ouvrir le dossier en mode WSL

**Méthode A - Depuis Windows :**

Dans VS Code :
1. `Ctrl+Shift+P`
2. Taper : `Remote-WSL: Open Folder in WSL`
3. Naviguer vers : `/mnt/c/projets/ApplyFlow/backend`
4. Cliquer **OK**

**Méthode B - Depuis WSL :**

```bash
wsl
cd /mnt/c/projets/ApplyFlow/backend
code .
```

---

## Vérifications

### ✅ WSL fonctionne
```powershell
wsl echo "Test OK"
```

### ✅ Code accessible depuis WSL
```powershell
wsl code --version
```

### ✅ Extension Remote-WSL installée

Dans VS Code, en bas à gauche, vous devriez voir un bouton vert **><** (Remote)

---

## Problèmes courants

### "Cannot connect to WSL"

**Cause :** Cache corrompu

**Solution :**
```powershell
wsl --shutdown
wsl rm -rf ~/.vscode-server
wsl rm -rf ~/.vscode-server-insiders
```

Puis rouvrir VS Code.

### "WSL 2 required"

**Cause :** Distribution en WSL 1

**Solution :**
```powershell
wsl --set-version Ubuntu 2
```

### Extension ne s'installe pas

**Cause :** Version VS Code obsolète

**Solution :**
1. Aide → Rechercher les mises à jour
2. Installer la dernière version
3. Redémarrer VS Code

### Terminal ne s'ouvre pas

**Cause :** Profil par défaut incorrect

**Solution :**

Dans VS Code settings.json :
```json
{
    "terminal.integrated.defaultProfile.windows": "PowerShell"
}
```

---

## Alternative : Remote SSH (si WSL ne fonctionne toujours pas)

1. Installer "Remote - SSH" dans VS Code
2. Configurer une connexion SSH localhost vers WSL
3. Se connecter via SSH au lieu de Remote-WSL

---

## Cas extrême : Réinitialisation complète

```powershell
# 1. Désinstaller VS Code
# 2. Supprimer les données
Remove-Item -Recurse -Force "$env:APPDATA\Code"
Remove-Item -Recurse -Force "$env:USERPROFILE\.vscode"

# 3. Dans WSL
wsl rm -rf ~/.vscode-server

# 4. Réinstaller VS Code
# 5. Réinstaller Remote-WSL
```

---

## 🎯 Configuration recommandée

Après connexion réussie, VS Code devrait afficher :

- En bas à gauche : **WSL: Ubuntu**
- Dans le terminal : Préfixe `(applyflow)`
- Explorer de fichiers : `/mnt/c/projets/ApplyFlow/backend`

---

## 📞 Besoin d'aide ?

Si aucune solution ne fonctionne :

1. Vérifier les logs : `Ctrl+Shift+P` → "Remote-WSL: Show Log"
2. Vérifier la console développeur : `Aide` → `Activer/désactiver les outils de développement`
3. Chercher les erreurs spécifiques

---

## ✨ Après résolution

Une fois connecté en WSL :

1. Sélectionner l'interpréteur Python : `Ctrl+Shift+P` → "Python: Select Interpreter"
2. Choisir : `~/miniconda3/envs/applyflow/bin/python`
3. Ouvrir un terminal : `Ctrl+ù`
4. Vérifier : Le prompt doit afficher `(applyflow)`

Vous êtes prêt ! 🚀
