# CropScan AI — Makefile

# Deployment Config
DOCKER_USER ?= $(shell docker info | grep Username | awk '{print $$2}' || echo "your-username")
IMAGE_NAME = cropscan-ai
TAG = latest

.PHONY: start dev down build logs restart setup-model download-dataset train help push release build-prod

start: build
	docker compose up -d
	@echo "\nCropScan AI running at http://localhost\n"

dev:
	docker compose up -d
	@echo "Dev mode active at http://localhost"

build:
	docker compose build

build-prod:
	docker build -t $(DOCKER_USER)/$(IMAGE_NAME):$(TAG) .
	@echo "\nProduction image built: $(DOCKER_USER)/$(IMAGE_NAME):$(TAG)\n"

tag:
	docker tag $(DOCKER_USER)/$(IMAGE_NAME):$(TAG) $(DOCKER_USER)/$(IMAGE_NAME):$(TAG)

push: build-prod
	docker push $(DOCKER_USER)/$(IMAGE_NAME):$(TAG)
	@echo "\nSuccessfully pushed to Docker Hub!\n"

down:
	docker compose down

restart:
	docker compose restart

restart-api:
	docker compose restart backend

logs:
	docker compose logs -f

setup-model: download-dataset
	DATASET_DIR=./backend/model/dataset/merged_dataset $(MAKE) train
	@echo "\nModel ready! Run 'make restart-api' to use it.\n"

download-dataset:
	pip install kagglehub && python backend/model/download_dataset.py $(KAGGLE_DATASETS)

train:
	cd backend/model && pip3 install tensorflow pillow numpy matplotlib python-dotenv && python3 train_model.py

clean:
	docker compose down -v --rmi local

help:
	@echo ""
	@echo "  CropScan AI — Commands"
	@echo "  make start           Build + start (local dev)"
	@echo "  make build-prod      Build production image"
	@echo "  make push            Build + push to Docker Hub"
	@echo "  make down            Stop all services"
	@echo "  make restart         Restart all services"
	@echo "  make logs            Stream logs"
	@echo "  make setup-model     Download dataset + train model"
	@echo "  make clean           Full cleanup"
	@echo ""
