# Script PowerShell pour réparer la connexion VS Code WSL

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Réparation VS Code WSL" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Vérifier WSL
Write-Host "1. Vérification de WSL..." -ForegroundColor Yellow
wsl --list --verbose
Write-Host ""

# 2. Redémarrer WSL
Write-Host "2. Redémarrage de WSL..." -ForegroundColor Yellow
wsl --shutdown
Start-Sleep -Seconds 3
wsl echo "WSL redémarré avec succès"
Write-Host ""

# 3. Nettoyer le cache VS Code WSL
Write-Host "3. Nettoyage du cache VS Code WSL..." -ForegroundColor Yellow
wsl rm -rf ~/.vscode-server
wsl rm -rf ~/.vscode-server-insiders
Write-Host "Cache nettoyé" -ForegroundColor Green
Write-Host ""

# 4. Ouvrir VS Code
Write-Host "4. Ouverture de VS Code en mode WSL..." -ForegroundColor Yellow
Set-Location "C:\projets\ApplyFlow\backend"
wsl -d Ubuntu -e bash -c "cd /mnt/c/projets/ApplyFlow/backend && code ."
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Si VS Code ne s'ouvre pas en mode WSL:" -ForegroundColor Yellow
Write-Host "1. Dans VS Code, appuyez sur Ctrl+Shift+P" -ForegroundColor White
Write-Host "2. Tapez: Remote-WSL: Reopen Folder in WSL" -ForegroundColor White
Write-Host "3. Sélectionnez: /mnt/c/projets/ApplyFlow/backend" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan

Read-Host "Appuyez sur Entrée pour continuer"
