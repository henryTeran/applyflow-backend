@echo off
echo ========================================
echo   Fixing VS Code WSL Connection
echo ========================================
echo.

echo 1. Checking WSL status...
wsl --list --verbose
echo.

echo 2. Restarting WSL server...
wsl --shutdown
timeout /t 3 /nobreak >nul
wsl echo "WSL restarted successfully"
echo.

echo 3. Cleaning VS Code WSL server cache...
wsl rm -rf ~/.vscode-server
echo Cache cleared
echo.

echo 4. Opening VS Code in WSL mode...
cd C:\projets\ApplyFlow\backend
wsl -d Ubuntu -e bash -c "cd /mnt/c/projets/ApplyFlow/backend && code ."
echo.

echo ========================================
echo If VS Code doesn't open in WSL mode:
echo 1. In VS Code, press Ctrl+Shift+P
echo 2. Type: "Remote-WSL: Reopen Folder in WSL"
echo 3. Select: /mnt/c/projets/ApplyFlow/backend
echo ========================================
pause
