@echo off
REM CropScan AI — Windows Setup
echo CropScan AI - Setup

docker --version >nul 2>&1
IF ERRORLEVEL 1 (echo ERROR: Docker not found. Install from https://docker.com & pause & exit /b 1)

docker compose version >nul 2>&1
IF ERRORLEVEL 1 (echo ERROR: Docker Compose not found. Update Docker Desktop. & pause & exit /b 1)

IF NOT EXIST .env (copy .env.example .env & echo Created .env)

echo Building containers (3-5 min on first run)...
docker compose up -d --build

echo.
echo CropScan AI running!
echo   App  -^> http://localhost
echo   Docs -^> http://localhost/api/docs
echo.
pause
