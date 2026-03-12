@echo off
REM ─────────────────────────────────────────────────────────────
REM  CropScan AI — Windows Setup Script
REM  Double-click this file or run: setup.bat
REM ─────────────────────────────────────────────────────────────

echo.
echo  CropScan AI - Setup
echo  --------------------------------

REM Check Docker
echo [1/4] Checking Docker...
docker --version >nul 2>&1
IF ERRORLEVEL 1 (
  echo  ERROR: Docker not found. Install from https://docker.com
  pause
  exit /b 1
)
echo  Docker is ready

REM Check Docker Compose
echo [2/4] Checking Docker Compose...
docker compose version >nul 2>&1
IF ERRORLEVEL 1 (
  echo  ERROR: Docker Compose not found. Update Docker Desktop.
  pause
  exit /b 1
)
echo  Docker Compose is ready

REM Setup .env
echo [3/4] Setting up environment...
IF NOT EXIST .env (
  copy .env.example .env
  echo  Created .env from .env.example
) ELSE (
  echo  .env already exists
)

REM Build and start
echo [4/4] Building and starting containers...
echo  This may take 3-5 minutes on first run...
docker compose -f docker-compose.yml up -d --build

echo.
echo  --------------------------------
echo  CropScan AI is running!
echo.
echo    App      -^> http://localhost
echo    API      -^> http://localhost:8000
echo    API Docs -^> http://localhost:8000/docs
echo.
echo  To stop: docker compose down
echo.
pause
