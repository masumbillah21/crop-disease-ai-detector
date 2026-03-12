"""
Crop Disease Detection - Prediction Utility
"""

import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import json
import os

# ─────────────────────────────────────────
# DISEASE INFO DATABASE
# ─────────────────────────────────────────
DISEASE_INFO = {
    "Apple___Apple_scab": {
        "display_name": "Apple Scab",
        "severity": "Moderate",
        "description": "Fungal disease causing dark, scabby lesions on leaves and fruits.",
        "treatment": [
            "Apply fungicide sprays during early spring",
            "Remove and destroy infected leaves",
            "Prune trees for better air circulation",
            "Use resistant apple varieties"
        ],
        "prevention": "Apply preventive fungicide before bud break"
    },
    "Apple___Black_rot": {
        "display_name": "Apple Black Rot",
        "severity": "High",
        "description": "Fungal infection causing fruit rot and leaf spot.",
        "treatment": [
            "Remove mummified fruits and dead wood",
            "Apply copper-based fungicides",
            "Maintain good sanitation practices"
        ],
        "prevention": "Regular pruning and removal of infected material"
    },
    "Apple___Cedar_apple_rust": {
        "display_name": "Cedar Apple Rust",
        "severity": "Moderate",
        "description": "Fungal disease with bright orange spots on leaves.",
        "treatment": [
            "Apply fungicides at bud break",
            "Remove nearby juniper/cedar trees if possible",
            "Use resistant apple varieties"
        ],
        "prevention": "Plant resistant varieties and apply preventive sprays"
    },
    "Apple___healthy": {
        "display_name": "Healthy Apple Plant",
        "severity": "None",
        "description": "The plant appears healthy with no signs of disease.",
        "treatment": ["No treatment needed"],
        "prevention": "Continue regular monitoring and good agricultural practices"
    },
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {
        "display_name": "Corn Gray Leaf Spot",
        "severity": "High",
        "description": "Fungal disease causing rectangular gray lesions on leaves.",
        "treatment": [
            "Apply foliar fungicides",
            "Rotate crops with non-host plants",
            "Use resistant hybrids"
        ],
        "prevention": "Crop rotation and residue management"
    },
    "Corn_(maize)___Common_rust_": {
        "display_name": "Corn Common Rust",
        "severity": "Moderate",
        "description": "Fungal disease with circular brown pustules on both leaf surfaces.",
        "treatment": [
            "Apply fungicides when rust is first detected",
            "Plant resistant varieties",
            "Monitor fields regularly"
        ],
        "prevention": "Use rust-resistant hybrid seeds"
    },
    "Tomato___Late_blight": {
        "display_name": "Tomato Late Blight",
        "severity": "Critical",
        "description": "Devastating disease causing water-soaked lesions and plant death.",
        "treatment": [
            "Apply copper-based fungicides immediately",
            "Remove and destroy infected plants",
            "Avoid overhead irrigation",
            "Apply chlorothalonil or mancozeb"
        ],
        "prevention": "Use certified disease-free seeds and resistant varieties"
    },
    "Tomato___healthy": {
        "display_name": "Healthy Tomato Plant",
        "severity": "None",
        "description": "The plant appears healthy with no signs of disease.",
        "treatment": ["No treatment needed"],
        "prevention": "Continue regular monitoring and proper watering"
    },
    "Potato___Late_blight": {
        "display_name": "Potato Late Blight",
        "severity": "Critical",
        "description": "The same pathogen that caused the Irish Famine. Rapid spreader.",
        "treatment": [
            "Apply fungicides (metalaxyl or chlorothalonil)",
            "Destroy infected plants immediately",
            "Do not compost infected material",
            "Harvest early if infection is severe"
        ],
        "prevention": "Use certified seed potatoes and resistant varieties"
    },
    "Potato___healthy": {
        "display_name": "Healthy Potato Plant",
        "severity": "None",
        "description": "The plant appears healthy with no signs of disease.",
        "treatment": ["No treatment needed"],
        "prevention": "Ensure proper spacing and drainage"
    }
}

SEVERITY_COLOR = {
    "None": "#2ecc71",
    "Moderate": "#f39c12",
    "High": "#e67e22",
    "Critical": "#e74c3c"
}


class CropDiseasePredictor:
    def __init__(self, model_path: str, class_names_path: str):
        print("🔄 Loading model...")
        self.model = tf.keras.models.load_model(model_path)
        with open(class_names_path, 'r') as f:
            self.class_names = json.load(f)
        print(f"✅ Model loaded | {len(self.class_names)} classes")

    def preprocess_image(self, img_path: str):
        img = image.load_img(img_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array / 255.0
        return img_array

    def predict(self, img_path: str):
        img_array = self.preprocess_image(img_path)
        predictions = self.model.predict(img_array, verbose=0)
        
        top5_indices = np.argsort(predictions[0])[-5:][::-1]
        top5 = [
            {
                "class": self.class_names[str(i)],
                "confidence": float(predictions[0][i])
            }
            for i in top5_indices
        ]

        best = top5[0]
        class_key = best["class"]
        info = DISEASE_INFO.get(class_key, {
            "display_name": class_key.replace("_", " ").replace("___", " - "),
            "severity": "Unknown",
            "description": "Disease information not available.",
            "treatment": ["Consult a local agricultural expert"],
            "prevention": "Regular monitoring recommended"
        })

        return {
            "prediction": class_key,
            "display_name": info["display_name"],
            "confidence": round(best["confidence"] * 100, 2),
            "severity": info["severity"],
            "severity_color": SEVERITY_COLOR.get(info["severity"], "#95a5a6"),
            "description": info["description"],
            "treatment": info["treatment"],
            "prevention": info["prevention"],
            "top5": top5
        }


# ─────────────────────────────────────────
# QUICK TEST
# ─────────────────────────────────────────
if __name__ == "__main__":
    predictor = CropDiseasePredictor(
        model_path="../crop_disease_model.h5",
        class_names_path="../class_names.json"
    )
    result = predictor.predict("test_leaf.jpg")
    print(f"\n🌿 Prediction: {result['display_name']}")
    print(f"📊 Confidence: {result['confidence']}%")
    print(f"⚠️  Severity: {result['severity']}")
    print(f"💊 Treatment: {result['treatment'][0]}")
