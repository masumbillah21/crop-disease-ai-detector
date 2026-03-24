#!/bin/bash
# CropScan AI — One-click Setup
set -e

echo "CropScan AI — Setup"

# Check Docker
command -v docker &> /dev/null || { echo "✗ Docker not found. Install from https://docker.com"; exit 1; }
docker info &> /dev/null || { echo "✗ Docker is not running. Start Docker Desktop."; exit 1; }

# Setup .env
[ ! -f .env ] && cp .env.example .env && echo "✓ Created .env"

# Build and start
echo "Building containers (3-5 min on first run)..."
docker compose up -d --build

echo ""
echo "CropScan AI running!"
echo "   App  → http://localhost"
echo "   Docs → http://localhost/api/docs"
echo ""
