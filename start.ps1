# ApplyFlow Backend - Lanceur PowerShell pour WSL
# Ce script facilite le lancement du serveur depuis Windows

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  ApplyFlow Backend (WSL + Conda)   " -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier si WSL est installé
$wslInstalled = Get-Command wsl -ErrorAction SilentlyContinue
if (-not $wslInstalled) {
    Write-Host "❌ WSL n'est pas installé sur ce système" -ForegroundColor Red
    Write-Host ""
    Write-Host "Pour installer WSL :" -ForegroundColor Yellow
    Write-Host "  wsl --install" -ForegroundColor White
    Write-Host ""
    Write-Host "Puis redémarrez votre ordinateur." -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "✅ WSL détecté" -ForegroundColor Green

# Chemin du projet dans WSL
$projectPath = "/mnt/c/projets/ApplyFlow/backend"

# Menu
Write-Host ""
Write-Host "Que voulez-vous faire ?" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Setup initial (première fois)" -ForegroundColor White
Write-Host "2. Démarrer le serveur" -ForegroundColor White
Write-Host "3. Charger des données de test" -ForegroundColor White
Write-Host "4. Ouvrir WSL dans le projet" -ForegroundColor White
Write-Host "5. Lancer les migrations" -ForegroundColor White
Write-Host "6. Quitter" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Votre choix (1-6)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "🚀 Lancement du setup initial..." -ForegroundColor Cyan
        Write-Host ""
        wsl -e bash -c "cd $projectPath && bash setup_wsl.sh"
    }
    "2" {
        Write-Host ""
        Write-Host "🚀 Démarrage du serveur..." -ForegroundColor Cyan
        Write-Host ""
        Write-Host "📍 API : http://localhost:8000" -ForegroundColor Green
        Write-Host "📚 Docs : http://localhost:8000/docs" -ForegroundColor Green
        Write-Host ""
        Write-Host "Appuyez sur Ctrl+C pour arrêter le serveur" -ForegroundColor Yellow
        Write-Host ""
        
        # Ouvrir le navigateur après 3 secondes
        Start-Job -ScriptBlock {
            Start-Sleep -Seconds 3
            Start-Process "http://localhost:8000/docs"
        } | Out-Null
        
        wsl -e bash -c "cd $projectPath && bash start.sh"
    }
    "3" {
        Write-Host ""
        Write-Host "🌱 Chargement des données de test..." -ForegroundColor Cyan
        Write-Host ""
        wsl -e bash -c "cd $projectPath && source ~/miniconda3/etc/profile.d/conda.sh && conda activate applyflow && python seed_data.py"
        Write-Host ""
        Write-Host "✅ Terminé !" -ForegroundColor Green
        pause
    }
    "4" {
        Write-Host ""
        Write-Host "🐧 Ouverture de WSL..." -ForegroundColor Cyan
        Write-Host ""
        wsl -e bash -c "cd $projectPath && exec bash"
    }
    "5" {
        Write-Host ""
        Write-Host "🔄 Lancement des migrations..." -ForegroundColor Cyan
        Write-Host ""
        wsl -e bash -c "cd $projectPath && source ~/miniconda3/etc/profile.d/conda.sh && conda activate applyflow && python migrate.py"
        Write-Host ""
        Write-Host "✅ Terminé !" -ForegroundColor Green
        pause
    }
    "6" {
        Write-Host "Au revoir !" -ForegroundColor Cyan
        exit 0
    }
    default {
        Write-Host "❌ Choix invalide" -ForegroundColor Red
        pause
    }
}
