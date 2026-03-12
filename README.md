# 🌿 CropScan AI — Crop Disease Detection System

An AI-powered web application that detects plant diseases from leaf photos using **MobileNetV2 transfer learning**, a **FastAPI backend**, and a **React analytics dashboard** — fully Dockerized for one-command deployment.

---

## 🚀 Quick Start (Docker — Recommended)

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
docker compose -f docker-compose.yml up -d --build
```

| Service      | URL                         |
|--------------|-----------------------------|
| 🌿 App       | http://localhost            |
| ⚡ API       | http://localhost:8000       |
| 📖 API Docs  | http://localhost:8000/docs  |

---

## ⚡ Common Commands

```bash
make start        # Build images + start (production)
make dev          # Start with hot reload (development)
make down         # Stop everything
make logs         # Stream live logs
make restart-api  # Restart backend after model update
make ps           # Show container status
make prune        # Full cleanup
make help         # See all commands
```

---

## 📁 Project Structure

```
crop-disease-detector/
│
├── 🐳 Docker & Config
│   ├── docker-compose.yml          ← Production orchestration
│   ├── docker-compose.override.yml ← Dev overrides (hot reload)
│   ├── .env.example                ← Environment template
│   ├── .gitignore
│   ├── Makefile                    ← Shortcut commands
│   ├── setup.sh                    ← One-click setup (Linux/Mac)
│   └── setup.bat                   ← One-click setup (Windows)
│
├── 🔀 nginx/
│   └── nginx.conf                  ← Reverse proxy (port 80)
│
├── 🧠 model/
│   ├── train_model.py              ← MobileNetV2 training script
│   ├── predict.py                  ← Prediction + disease info DB
│   ├── class_names.json            ← 38-class index (demo included)
│   └── dataset/                    ← Place PlantVillage data here
│
├── ⚙️  backend/
│   ├── Dockerfile                  ← Multi-stage Python 3.11 slim
│   ├── main.py                     ← FastAPI server
│   ├── predict.py                  ← Prediction engine copy
│   └── requirements.txt
│
└── 🎨 frontend/
    ├── Dockerfile                  ← Node 20 build → Nginx serve
    ├── nginx.conf                  ← Frontend nginx config
    ├── src/
    │   ├── App.jsx                 ← Full React UI (Scan/History/Dashboard)
    │   └── main.jsx
    ├── index.html
    ├── package.json
    └── vite.config.js
```

---

## 🏗️ Docker Architecture

```
Browser
   │
   ▼  :80
┌─────────────────┐
│   Nginx Proxy   │ ← routes traffic
└────────┬────────┘
         │                │
    /api/*              /*
         │                │
    ┌────▼─────┐   ┌──────▼──────┐
    │ FastAPI  │   │ React/Nginx │
    │  :8000   │   │    :80      │
    └──────────┘   └─────────────┘
```

---

## 🧠 Add Your Trained Model

Once you've trained the model, drop the files into `model/`:

```
model/
├── crop_disease_model.h5   ← trained model (~14MB)
└── class_names.json        ← already included
```

Then reload the backend:
```bash
make restart-api
```

The API auto-detects the model file and **switches from demo → real predictions**.

---

## 🏋️ Train the Model

```bash
# 1. Download dataset from Kaggle:
#    https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset
#    Extract to: model/dataset/plantvillage/

# 2. Train (locally, ~30-60 min with GPU):
make train

# Outputs: model/crop_disease_model.h5
```

---

## 🌐 API Reference

| Method | Endpoint     | Description                      |
|--------|--------------|----------------------------------|
| GET    | `/`          | API info & status                |
| GET    | `/health`    | Health check + mode (demo/prod)  |
| POST   | `/predict`   | Upload image → disease diagnosis |
| GET    | `/diseases`  | All 38 supported disease classes |
| GET    | `/stats`     | Dashboard analytics data         |

### Sample `/predict` Response
```json
{
  "display_name": "Tomato Late Blight",
  "confidence": 94.3,
  "severity": "Critical",
  "severity_color": "#e74c3c",
  "description": "Devastating disease causing water-soaked lesions...",
  "treatment": ["Apply copper-based fungicides immediately", "..."],
  "prevention": "Use certified disease-free seeds...",
  "top5": [{"class": "Tomato___Late_blight", "confidence": 0.943}, "..."],
  "processing_time_ms": 143,
  "demo_mode": false
}
```

---

## 🌱 Supported Plants & Diseases (38 classes)

| Plant       | Diseases Detected                                     |
|-------------|-------------------------------------------------------|
| 🍎 Apple    | Scab, Black Rot, Cedar Rust, Healthy                  |
| 🌽 Corn     | Gray Leaf Spot, Common Rust, Northern Blight, Healthy |
| 🍇 Grape    | Black Rot, Esca, Leaf Blight, Healthy                 |
| 🥔 Potato   | Early Blight, Late Blight, Healthy                    |
| 🍅 Tomato   | Late/Early Blight, Leaf Mold, Mosaic Virus + 4 more  |
| + 9 more    | Peach, Pepper, Strawberry, Squash, Soybean...         |

---

## 🛠️ Tech Stack

| Layer     | Technology                          |
|-----------|-------------------------------------|
| ML Model  | TensorFlow 2.15 + MobileNetV2       |
| Backend   | FastAPI + Uvicorn (Python 3.11)     |
| Frontend  | React 18 + Vite + Recharts          |
| Proxy     | Nginx 1.25                          |
| Container | Docker + Docker Compose             |

---

## 📊 Expected Model Performance

| Metric              | Value      |
|---------------------|------------|
| Validation Accuracy | ~95–97%    |
| Inference Time      | ~100–200ms |
| Model Size          | ~14MB      |
| Classes Supported   | 38         |

---

Made with 🌿 for AI Capstone Project
