# 🚀 VS Code + WSL Setup Guide

## Étape 1 : Installer Miniconda dans WSL

Ouvrez WSL et exécutez :

```bash
cd /mnt/c/projets/ApplyFlow/backend
bash install_miniconda.sh
```

Puis **fermez et rouvrez** le terminal WSL.

## Étape 2 : Créer l'environnement Conda

```bash
cd /mnt/c/projets/ApplyFlow/backend
conda env create -f environment.yml
conda activate applyflow
```

## Étape 3 : Ouvrir le projet dans VS Code avec WSL

### Option A : Depuis VS Code Windows

1. Ouvrez VS Code
2. Installez l'extension **Remote - WSL** si ce n'est pas déjà fait
3. Appuyez sur `F1` → `Remote-WSL: Open Folder in WSL`
4. Naviguez vers `/mnt/c/projets/ApplyFlow/backend`
5. Cliquez sur **OK**

### Option B : Depuis le terminal WSL

```bash
cd /mnt/c/projets/ApplyFlow/backend
code .
```

VS Code s'ouvrira automatiquement en mode WSL.

## Étape 4 : Sélectionner l'interpréteur Python

1. Dans VS Code, appuyez sur `Ctrl+Shift+P`
2. Tapez `Python: Select Interpreter`
3. Choisissez : `Python 3.11.x ('applyflow')`
   - Chemin : `~/miniconda3/envs/applyflow/bin/python`

## Étape 5 : Vérifier la configuration

Ouvrez un nouveau terminal dans VS Code (`Ctrl+ù`).

Vous devriez voir :
```
(applyflow) user@hostname:/mnt/c/projets/ApplyFlow/backend$
```

Le préfixe `(applyflow)` indique que l'environnement conda est activé.

## Étape 6 : Lancer le serveur

Dans le terminal VS Code :

```bash
./start.sh
```

Ou utilisez le debugger VS Code (`F5`) pour lancer en mode debug.

## 🔧 Raccourcis VS Code utiles

- `F5` : Lancer le debugger
- `Ctrl+ù` : Ouvrir/fermer le terminal
- `Ctrl+Shift+P` : Palette de commandes
- `Ctrl+Shift+L` : Sélectionner toutes les occurrences
- `Alt+Shift+F` : Formater le code

## 📁 Structure du workspace

Le fichier `applyflow.code-workspace` contient toute la configuration.

Pour l'ouvrir :
- Fichier → Ouvrir le workspace...
- Sélectionnez `applyflow.code-workspace`

## 🐛 Dépannage

### L'interpréteur Python n'apparaît pas

```bash
# Dans WSL
which python
# Devrait afficher : /home/user/miniconda3/envs/applyflow/bin/python
```

Rechargez VS Code : `Ctrl+Shift+P` → `Developer: Reload Window`

### Le terminal n'active pas conda

Ajoutez à `~/.bashrc` :

```bash
# >>> conda initialize >>>
# ... (déjà fait par install_miniconda.sh)
# <<< conda initialize <<<

# Auto-activate applyflow
if [ -f ~/miniconda3/etc/profile.d/conda.sh ]; then
    . ~/miniconda3/etc/profile.d/conda.sh
    conda activate applyflow
fi
```

### VS Code ne se connecte pas à WSL

Vérifiez que WSL fonctionne :

```powershell
wsl --list --verbose
```

Redémarrez WSL si nécessaire :

```powershell
wsl --shutdown
wsl
```

## 🎉 C'est prêt !

Vous pouvez maintenant développer avec :
- IntelliSense Python complet
- Auto-complétion
- Debugger intégré
- Tests intégrés
- Format automatique du code
- Linting en temps réel

Bon développement ! 🚀
