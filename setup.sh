#!/bin/bash
# ─────────────────────────────────────────────────────────────
#  CropScan AI — One-click Setup Script
#  Usage: chmod +x setup.sh && ./setup.sh
# ─────────────────────────────────────────────────────────────

set -e  # Exit on error

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo -e "${GREEN}🌿  CropScan AI — Setup${NC}"
echo "────────────────────────────────"

# ── Check Docker ──────────────────────────────────────────────
echo -e "\n${CYAN}[1/4] Checking Docker...${NC}"
if ! command -v docker &> /dev/null; then
  echo -e "${RED}✗ Docker not found. Install from https://docker.com${NC}"
  exit 1
fi
if ! docker info &> /dev/null; then
  echo -e "${RED}✗ Docker daemon is not running. Please start Docker Desktop.${NC}"
  exit 1
fi
echo -e "${GREEN}✓ Docker is ready${NC}"

# ── Check Docker Compose ──────────────────────────────────────
echo -e "\n${CYAN}[2/4] Checking Docker Compose...${NC}"
if ! docker compose version &> /dev/null; then
  echo -e "${RED}✗ Docker Compose not found. Update Docker Desktop.${NC}"
  exit 1
fi
echo -e "${GREEN}✓ Docker Compose is ready${NC}"

# ── Copy .env if missing ──────────────────────────────────────
echo -e "\n${CYAN}[3/4] Setting up environment...${NC}"
if [ ! -f .env ]; then
  cp .env.example .env
  echo -e "${GREEN}✓ Created .env from .env.example${NC}"
else
  echo -e "${GREEN}✓ .env already exists${NC}"
fi

# ── Build and Start ───────────────────────────────────────────
echo -e "\n${CYAN}[4/4] Building and starting containers...${NC}"
echo -e "${YELLOW}  This may take 3–5 minutes on first run (downloading base images)${NC}\n"

docker compose -f docker-compose.yml up -d --build

# ── Done ──────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}────────────────────────────────${NC}"
echo -e "${GREEN}✅  CropScan AI is running!${NC}"
echo ""
echo -e "   ${CYAN}🌿 App      →${NC} http://localhost"
echo -e "   ${CYAN}⚡ API      →${NC} http://localhost:8000"
echo -e "   ${CYAN}📖 API Docs →${NC} http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}To stop:   docker compose down${NC}"
echo -e "${YELLOW}To logs:   docker compose logs -f${NC}"
echo -e "${YELLOW}More help: make help${NC}"
echo ""
