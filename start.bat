@echo off
REM ApplyFlow Backend - Lanceur Windows pour WSL
REM Double-cliquez sur ce fichier pour démarrer

echo =====================================
echo   ApplyFlow Backend (WSL + Conda)
echo =====================================
echo.

REM Vérifier si WSL est installé
wsl --status >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] WSL n'est pas installe
    echo.
    echo Pour installer WSL :
    echo   wsl --install
    echo.
    echo Puis redemarrez votre ordinateur.
    pause
    exit /b 1
)

echo [OK] WSL detecte
echo.

REM Menu
echo Que voulez-vous faire ?
echo.
echo 1. Setup initial (premiere fois)
echo 2. Demarrer le serveur
echo 3. Charger des donnees de test
echo 4. Ouvrir WSL dans le projet
echo 5. Lancer les migrations
echo 6. Quitter
echo.

set /p choice="Votre choix (1-6) : "

if "%choice%"=="1" goto setup
if "%choice%"=="2" goto start
if "%choice%"=="3" goto seed
if "%choice%"=="4" goto wsl
if "%choice%"=="5" goto migrate
if "%choice%"=="6" goto quit
goto invalid

:setup
echo.
echo Lancement du setup initial...
echo.
wsl -e bash -c "cd /mnt/c/projets/ApplyFlow/backend && bash setup_wsl.sh"
pause
goto end

:start
echo.
echo Demarrage du serveur...
echo.
echo API : http://localhost:8000
echo Docs : http://localhost:8000/docs
echo.
echo Appuyez sur Ctrl+C pour arreter le serveur
echo.
timeout /t 3 /nobreak >nul
start http://localhost:8000/docs
wsl -e bash -c "cd /mnt/c/projets/ApplyFlow/backend && bash start.sh"
goto end

:seed
echo.
echo Chargement des donnees de test...
echo.
wsl -e bash -c "cd /mnt/c/projets/ApplyFlow/backend && source ~/miniconda3/etc/profile.d/conda.sh && conda activate applyflow && python seed_data.py"
echo.
echo [OK] Termine !
pause
goto end

:wsl
echo.
echo Ouverture de WSL...
echo.
wsl -e bash -c "cd /mnt/c/projets/ApplyFlow/backend && exec bash"
goto end

:migrate
echo.
echo Lancement des migrations...
echo.
wsl -e bash -c "cd /mnt/c/projets/ApplyFlow/backend && source ~/miniconda3/etc/profile.d/conda.sh && conda activate applyflow && python migrate.py"
echo.
echo [OK] Termine !
pause
goto end

:quit
echo Au revoir !
goto end

:invalid
echo [ERREUR] Choix invalide
pause
goto end

:end
