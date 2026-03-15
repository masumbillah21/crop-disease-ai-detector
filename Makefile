# ─────────────────────────────────────────────────────────────
#  CropScan AI — Makefile
#  Usage: make <target>
# ─────────────────────────────────────────────────────────────

.PHONY: up down build start stop restart logs logs-api logs-ui ps clean prune shell-api shell-ui env-setup train help

build:
	docker compose -f docker-compose.yml build --no-cache

up:
	docker compose -f docker-compose.yml up -d
	@echo ""
	@echo "✅  CropScan AI is running!"
	@echo "   🌿 App  → http://localhost"
	@echo "   ⚡ API  → http://localhost:8000"
	@echo "   📖 Docs → http://localhost:8000/docs"
	@echo ""

start: build up

dev:
	docker compose up -d
	@echo "🔧 Dev mode active"

down:
	docker compose down

stop: down

restart:
	docker compose restart

restart-api:
	docker compose restart backend

logs:
	docker compose logs -f

logs-api:
	docker compose logs -f backend

logs-ui:
	docker compose logs -f frontend

logs-proxy:
	docker compose logs -f nginx

ps:
	docker compose ps

shell-api:
	docker compose exec backend /bin/bash

shell-ui:
	docker compose exec frontend /bin/sh

env-setup:
	@if [ ! -f .env ]; then cp .env.example .env && echo "✅ .env created"; else echo "⚠️  .env already exists"; fi

train:
	cd model && pip install tensorflow pillow numpy matplotlib && python train_model.py

download-dataset:
	pip install kagglehub
	python model/download_dataset.py

clean:
	docker compose down -v

prune:
	docker compose down -v --rmi local

help:
	@echo ""
	@echo "  🌿 CropScan AI — Commands"
	@echo "  make start        Build + start (production)"
	@echo "  make dev          Start with hot reload"
	@echo "  make up           Start with cached images"
	@echo "  make down         Stop all services"
	@echo "  make restart      Restart all services"
	@echo "  make restart-api  Restart backend only"
	@echo "  make build        Rebuild all images"
	@echo "  make logs         Stream all logs"
	@echo "  make logs-api     Backend logs"
	@echo "  make ps           Container status"
	@echo "  make shell-api    Shell into backend"
	@echo "  make shell-ui     Shell into frontend"
	@echo "  make env-setup    Create .env file"
	@echo "  make download-dataset Download PlantVillage dataset"
	@echo "  make train        Train ML model locally"
	@echo "  make clean        Remove containers + volumes"
	@echo "  make prune        Full wipe"
	@echo ""
