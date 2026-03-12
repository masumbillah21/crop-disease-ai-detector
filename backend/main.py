"""
Crop Disease Detection - FastAPI Backend
Run: uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image as keras_image
import json
import io
import os
import time
from PIL import Image
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "model"))
from predict import CropDiseasePredictor, DISEASE_INFO

# ─────────────────────────────────────────
# APP SETUP
# ─────────────────────────────────────────
app = FastAPI(
    title="🌿 Crop Disease Detector API",
    description="AI-powered crop disease detection using MobileNetV2",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────
# LOAD MODEL ON STARTUP
# ─────────────────────────────────────────
MODEL_PATH = os.getenv("MODEL_PATH", "../crop_disease_model.h5")
CLASS_NAMES_PATH = os.getenv("CLASS_NAMES_PATH", "../class_names.json")

predictor = None

@app.on_event("startup")
async def load_model():
    global predictor
    try:
        predictor = CropDiseasePredictor(MODEL_PATH, CLASS_NAMES_PATH)
        print("✅ Model loaded successfully")
    except Exception as e:
        print(f"⚠️  Model not found: {e}")
        print("⚠️  Running in DEMO mode with mock predictions")

# ─────────────────────────────────────────
# MOCK DEMO DATA (when model not available)
# ─────────────────────────────────────────
DEMO_PREDICTIONS = [
    {
        "prediction": "Tomato___Late_blight",
        "display_name": "Tomato Late Blight",
        "confidence": 94.3,
        "severity": "Critical",
        "severity_color": "#e74c3c",
        "description": "Devastating disease causing water-soaked lesions and plant death.",
        "treatment": [
            "Apply copper-based fungicides immediately",
            "Remove and destroy infected plants",
            "Avoid overhead irrigation",
            "Apply chlorothalonil or mancozeb"
        ],
        "prevention": "Use certified disease-free seeds and resistant varieties",
        "top5": [
            {"class": "Tomato___Late_blight", "confidence": 0.943},
            {"class": "Tomato___Early_blight", "confidence": 0.032},
            {"class": "Tomato___healthy", "confidence": 0.015},
            {"class": "Potato___Late_blight", "confidence": 0.007},
            {"class": "Tomato___Leaf_Mold", "confidence": 0.003}
        ]
    },
    {
        "prediction": "Apple___Apple_scab",
        "display_name": "Apple Scab",
        "confidence": 88.7,
        "severity": "Moderate",
        "severity_color": "#f39c12",
        "description": "Fungal disease causing dark, scabby lesions on leaves and fruits.",
        "treatment": [
            "Apply fungicide sprays during early spring",
            "Remove and destroy infected leaves",
            "Prune trees for better air circulation"
        ],
        "prevention": "Apply preventive fungicide before bud break",
        "top5": [
            {"class": "Apple___Apple_scab", "confidence": 0.887},
            {"class": "Apple___Black_rot", "confidence": 0.071},
            {"class": "Apple___Cedar_apple_rust", "confidence": 0.028},
            {"class": "Apple___healthy", "confidence": 0.009},
            {"class": "Cherry___Powdery_mildew", "confidence": 0.005}
        ]
    },
    {
        "prediction": "Apple___healthy",
        "display_name": "Healthy Apple Plant",
        "confidence": 97.1,
        "severity": "None",
        "severity_color": "#2ecc71",
        "description": "The plant appears healthy with no signs of disease.",
        "treatment": ["No treatment needed"],
        "prevention": "Continue regular monitoring and good agricultural practices",
        "top5": [
            {"class": "Apple___healthy", "confidence": 0.971},
            {"class": "Apple___Apple_scab", "confidence": 0.018},
            {"class": "Apple___Black_rot", "confidence": 0.007},
            {"class": "Apple___Cedar_apple_rust", "confidence": 0.003},
            {"class": "Cherry___healthy", "confidence": 0.001}
        ]
    }
]

demo_counter = 0

# ─────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "message": "🌿 Crop Disease Detector API",
        "status": "running",
        "model_loaded": predictor is not None,
        "endpoints": {
            "predict": "POST /predict",
            "health": "GET /health",
            "diseases": "GET /diseases",
            "stats": "GET /stats"
        }
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model_loaded": predictor is not None,
        "mode": "production" if predictor else "demo"
    }


@app.post("/predict")
async def predict_disease(file: UploadFile = File(...)):
    global demo_counter

    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image (JPEG, PNG, WebP)")

    # Validate file size (max 10MB)
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image too large. Max size: 10MB")

    start_time = time.time()

    try:
        if predictor:
            # Real prediction
            img = Image.open(io.BytesIO(contents)).convert("RGB")
            img = img.resize((224, 224))
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)

            predictions = predictor.model.predict(img_array, verbose=0)
            top5_indices = np.argsort(predictions[0])[-5:][::-1]
            top5 = [
                {"class": predictor.class_names[str(i)], "confidence": float(predictions[0][i])}
                for i in top5_indices
            ]
            best_class = top5[0]["class"]
            confidence = round(top5[0]["confidence"] * 100, 2)

            from predict import DISEASE_INFO, SEVERITY_COLOR
            info = DISEASE_INFO.get(best_class, {
                "display_name": best_class.replace("___", " - ").replace("_", " "),
                "severity": "Unknown",
                "description": "Disease information not available.",
                "treatment": ["Consult a local agricultural expert"],
                "prevention": "Regular monitoring recommended"
            })

            result = {
                "prediction": best_class,
                "display_name": info["display_name"],
                "confidence": confidence,
                "severity": info["severity"],
                "severity_color": SEVERITY_COLOR.get(info["severity"], "#95a5a6"),
                "description": info["description"],
                "treatment": info["treatment"],
                "prevention": info["prevention"],
                "top5": top5
            }
        else:
            # Demo mode - cycle through predictions
            result = DEMO_PREDICTIONS[demo_counter % len(DEMO_PREDICTIONS)]
            demo_counter += 1
            time.sleep(0.5)  # Simulate processing

        processing_time = round((time.time() - start_time) * 1000)

        return JSONResponse({
            **result,
            "processing_time_ms": processing_time,
            "filename": file.filename,
            "demo_mode": predictor is None
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.get("/diseases")
async def get_diseases():
    """Get all supported diseases with info"""
    return {
        "count": len(DISEASE_INFO),
        "diseases": [
            {
                "key": k,
                "display_name": v["display_name"],
                "severity": v["severity"],
                "description": v["description"]
            }
            for k, v in DISEASE_INFO.items()
        ]
    }


@app.get("/stats")
async def get_stats():
    """Mock stats for dashboard"""
    return {
        "total_scans": 1247,
        "diseases_detected": 892,
        "healthy_plants": 355,
        "accuracy": 96.4,
        "most_common": [
            {"name": "Tomato Late Blight", "count": 234, "percentage": 26.2},
            {"name": "Apple Scab", "count": 189, "percentage": 21.2},
            {"name": "Corn Gray Leaf Spot", "count": 156, "percentage": 17.5},
            {"name": "Potato Late Blight", "count": 143, "percentage": 16.0},
            {"name": "Corn Common Rust", "count": 98, "percentage": 11.0},
            {"name": "Others", "count": 72, "percentage": 8.1}
        ],
        "recent_scans": [
            {"date": "Mon", "scans": 45, "diseased": 32},
            {"date": "Tue", "scans": 67, "diseased": 48},
            {"date": "Wed", "scans": 89, "diseased": 61},
            {"date": "Thu", "scans": 123, "diseased": 87},
            {"date": "Fri", "scans": 98, "diseased": 71},
            {"date": "Sat", "scans": 76, "diseased": 54},
            {"date": "Sun", "scans": 54, "diseased": 39}
        ],
        "severity_breakdown": [
            {"severity": "Critical", "count": 178, "color": "#e74c3c"},
            {"severity": "High", "count": 267, "color": "#e67e22"},
            {"severity": "Moderate", "count": 447, "color": "#f39c12"},
            {"severity": "Healthy", "count": 355, "color": "#2ecc71"}
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
