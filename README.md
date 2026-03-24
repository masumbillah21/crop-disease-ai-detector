# CropScan AI — Crop Disease Detection System

AI-powered web application that detects plant diseases from leaf photos using **MobileNetV2**, **FastAPI**, and **React** — fully Dockerized.

---

## Quick Start

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

### Linux / macOS
```bash
chmod +x setup.sh && ./setup.sh
```

### Windows
```
Double-click setup.bat
```

### Manual
```bash
cp .env.example .env
docker compose up -d --build
```

| Service     | URL                        |
|-------------|----------------------------|
| App         | http://localhost           |
| API         | http://localhost/api       |
| API Docs    | http://localhost/api/docs  |

---

## Commands

```bash
make start        # Build + start
make dev          # Start (cached images)
make down         # Stop everything
make logs         # Stream logs
make restart-api  # Restart backend after model update
make train        # Train ML model
make help         # All commands
```

---

## Project Structure

```
crop-disease-docker/
├── docker-compose.yml         ← 2-service orchestration
├── .env.example               ← Environment template
├── Makefile                   ← Shortcut commands
├── setup.sh / setup.bat       ← One-click setup
│
├── backend/
│   ├── Dockerfile             ← Multi-stage Python 3.11
│   ├── main.py                ← FastAPI server
│   ├── demo_data.json         ← Demo mode mock data
│   ├── requirements.txt
│   └── model/
│       ├── predict.py         ← Prediction engine
│       ├── disease_info.json  ← Disease database (10 diseases)
│       ├── class_names.json   ← 38-class index
│       ├── train_model.py     ← MobileNetV2 training script
│       └── download_dataset.py
│
└── frontend/
    ├── Dockerfile             ← Node 20 build → Nginx serve
    ├── nginx.conf             ← Proxy: /api → backend:8000
    ├── src/App.jsx            ← React UI (Scan/History/Dashboard)
    └── package.json
```

---

## Architecture

```
Browser → :80
     ┌────────────────┐
     │ Frontend Nginx  │ ← serves React + proxies /api
     └───────┬────────┘
             │ /api/*
       ┌─────▼──────┐
       │  FastAPI    │
       │  backend    │
       └─────────────┘
```

---

## Add Your Trained Model

Drop files into `backend/model/`:
```
backend/model/
├── crop_disease_model.h5   ← trained model (~14MB)
└── class_names.json        ← already included
```

Then: `make restart-api`

---

## API Reference

| Method | Endpoint     | Description                      |
|--------|--------------|----------------------------------|
| GET    | `/`          | API info & status                |
| GET    | `/health`    | Health check + mode (demo/prod)  |
| POST   | `/predict`   | Upload image → disease diagnosis |
| GET    | `/diseases`  | All supported disease classes    |
| GET    | `/stats`     | Dashboard analytics data         |

---

## Supported Plants & Diseases (38 classes)

| Plant       | Diseases Detected                                     |
|-------------|-------------------------------------------------------|
| Apple       | Scab, Black Rot, Cedar Rust, Healthy                  |
| Corn        | Gray Leaf Spot, Common Rust, Northern Blight, Healthy |
| Grape       | Black Rot, Esca, Leaf Blight, Healthy                 |
| Potato      | Early Blight, Late Blight, Healthy                    |
| Tomato      | Late/Early Blight, Leaf Mold, Mosaic Virus + 4 more  |
| + 9 more    | Peach, Pepper, Strawberry, Squash, Soybean...         |

---

## Tech Stack

| Layer     | Technology                      |
|-----------|---------------------------------|
| ML Model  | TensorFlow 2.15 + MobileNetV2  |
| Backend   | FastAPI + Uvicorn (Python 3.11) |
| Frontend  | React 18 + Vite + Recharts     |
| Proxy     | Nginx (inside frontend container) |
| Container | Docker + Docker Compose         |

