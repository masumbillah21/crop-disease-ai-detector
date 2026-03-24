# CropScan AI — Makefile

.PHONY: start dev down build logs restart train download-dataset help

start: build
	docker compose up -d
	@echo "\nCropScan AI running at http://localhost\n"

dev:
	docker compose up -d
	@echo "Dev mode active at http://localhost"

build:
	docker compose build

down:
	docker compose down

restart:
	docker compose restart

restart-api:
	docker compose restart backend

logs:
	docker compose logs -f

train:
	cd backend/model && pip install tensorflow pillow numpy matplotlib && python train_model.py

download-dataset:
	pip install kagglehub && python backend/model/download_dataset.py

clean:
	docker compose down -v --rmi local

help:
	@echo ""
	@echo "  CropScan AI — Commands"
	@echo "  make start           Build + start"
	@echo "  make dev             Start (cached images)"
	@echo "  make down            Stop all services"
	@echo "  make restart         Restart all services"
	@echo "  make restart-api     Restart backend only"
	@echo "  make logs            Stream logs"
	@echo "  make train           Train ML model"
	@echo "  make download-dataset  Download dataset"
	@echo "  make clean           Full cleanup"
	@echo ""
