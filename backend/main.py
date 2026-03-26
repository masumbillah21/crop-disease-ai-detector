"""
Crop Disease Detection - FastAPI Backend
Run: uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
from collections import Counter
from datetime import datetime
import io
import os
import sys
import json
import time
from pathlib import Path
import config

# Import predictor from model directory
sys.path.insert(0, str(Path(__file__).parent / "model"))
from predict import CropDiseasePredictor, DISEASE_INFO

# ─── Load demo data ──────────────────────────────────────────
with open(Path(__file__).parent / "demo_data.json") as f:
    _demo = json.load(f)
DEMO_PREDICTIONS = _demo["predictions"]

# ─── App Setup ────────────────────────────────────────────────
app = FastAPI(
    title="Crop Disease Detector API",
    description="AI-powered crop disease detection using MobileNetV2",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Load Model ───────────────────────────────────────────────
MODEL_PATH = config.MODEL_PATH
CLASS_NAMES_PATH = config.CLASS_NAMES_PATH
predictor = None
model_error = None
demo_counter = 0

# ─── Scan Tracking (in-memory) ────────────────────────────────
scan_history = []  # list of {"name", "severity", "confidence", "timestamp"}

@app.on_event("startup")
async def load_model():
    global predictor, model_error
    try:
        # Try SavedModel directory first
        predictor = CropDiseasePredictor(MODEL_PATH, CLASS_NAMES_PATH)
    except Exception as e1:
        model_error = f"SavedModel load failed: {str(e1)}"
        try:
            # Fallback to .h5 if it exists
            h5_path = f"{MODEL_PATH}.h5"
            if os.path.exists(h5_path):
                predictor = CropDiseasePredictor(h5_path, CLASS_NAMES_PATH)
                model_error = None # Success
        except Exception as e2:
            model_error = f"Both load methods failed. 1: {str(e1)} | 2: {str(e2)}"
            print(f"Model error: {model_error}")

# ─── Endpoints ────────────────────────────────────────────────
@app.get("/api", include_in_schema=False)
@app.get("/api/", include_in_schema=False)
async def root():
    return {
        "message": "Crop Disease Detector API",
        "status": "running",
        "model_loaded": predictor is not None,
        "endpoints": ["POST /predict", "GET /health", "GET /diseases", "GET /stats"]
    }

@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "model_loaded": predictor is not None,
        "mode": "production" if predictor else "demo",
        "error": model_error
    }

@app.post("/api/predict")
async def predict_disease(file: UploadFile = File(...)):
    global demo_counter

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image (JPEG, PNG, WebP)")

    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(400, "Image too large. Max size: 10MB")

    start = time.time()
    try:
        if predictor:
            img = Image.open(io.BytesIO(contents))
            result = predictor.predict_from_image(img)
        else:
            result = DEMO_PREDICTIONS[demo_counter % len(DEMO_PREDICTIONS)]
            demo_counter += 1
            time.sleep(0.5)

        # Track this scan
        scan_history.append({
            "name": result["display_name"],
            "severity": result["severity"],
            "confidence": result["confidence"],
            "timestamp": datetime.now().isoformat()
        })

        return JSONResponse({
            **result,
            "processing_time_ms": round((time.time() - start) * 1000),
            "filename": file.filename,
            "demo_mode": predictor is None
        })
    except Exception as e:
        raise HTTPException(500, f"Prediction failed: {str(e)}")

@app.get("/api/diseases")
async def get_diseases():
    return {
        "count": len(DISEASE_INFO),
        "diseases": [
            {"key": k, "display_name": v["display_name"],
             "severity": v["severity"], "description": v["description"]}
            for k, v in DISEASE_INFO.items()
        ]
    }


@app.get("/api/stats")
async def get_stats():
    """Real stats computed from actual scans."""
    total = len(scan_history)
    if total == 0:
        return {
            "total_scans": 0,
            "diseases_detected": 0,
            "healthy_plants": 0,
            "accuracy": 0,
            "most_common": [],
            "recent_scans": [],
            "severity_breakdown": []
        }

    diseases = [s for s in scan_history if s["severity"] != "None"]
    healthy = [s for s in scan_history if s["severity"] == "None"]

    # Most common diseases
    name_counts = Counter(s["name"] for s in scan_history)
    most_common = [
        {"name": name, "count": count, "percentage": round(count / total * 100, 1)}
        for name, count in name_counts.most_common(6)
    ]

    # Severity breakdown
    sev_counts = Counter(s["severity"] for s in scan_history)
    sev_colors = {"None": "#2ecc71", "Moderate": "#f39c12", "High": "#e67e22", "Critical": "#e74c3c"}
    severity_breakdown = [
        {"severity": "Healthy" if sev == "None" else sev,
         "count": count, "color": sev_colors.get(sev, "#95a5a6")}
        for sev, count in sev_counts.items()
    ]

    # Recent scans grouped by date
    date_counts = Counter()
    date_diseased = Counter()
    for s in scan_history:
        day = datetime.fromisoformat(s["timestamp"]).strftime("%a")
        date_counts[day] += 1
        if s["severity"] != "None":
            date_diseased[day] += 1
    recent_scans = [
        {"date": day, "scans": date_counts[day], "diseased": date_diseased.get(day, 0)}
        for day in date_counts
    ]

    avg_confidence = round(sum(s["confidence"] for s in scan_history) / total, 1)

    return {
        "total_scans": total,
        "diseases_detected": len(diseases),
        "healthy_plants": len(healthy),
        "accuracy": avg_confidence,
        "most_common": most_common,
        "recent_scans": recent_scans,
        "severity_breakdown": severity_breakdown
    }

# ─── Serve Frontend (Must be last) ───────────────────────────
static_path = Path(__file__).parent / "static"
if static_path.exists():
    # Fallback for SPA routing: serve index.html for unknown routes
    @app.exception_handler(404)
    async def custom_404_handler(request, exc):
        # If it's an API route that truly doesn't exist, return 404 JSON
        if request.url.path.startswith("/api"):
             return JSONResponse(
                 status_code=404,
                 content={"detail": "API route not found. See /api/docs for help."}
             )
        # Otherwise, it's a frontend route (SPA)
        return FileResponse(static_path / "index.html")

    app.mount("/", StaticFiles(directory=str(static_path), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=config.PORT)
