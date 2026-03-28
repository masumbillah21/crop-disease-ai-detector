"""
Crop Disease Detection - Prediction Engine
Single source of truth for model loading, preprocessing, and inference.
"""

import numpy as np
import tensorflow as tf
import json
import os
import sys
from pathlib import Path

# Add backend dir to sys.path for standalone execution
sys.path.append(str(Path(__file__).parent.parent))
import config


# Load disease info from JSON
_DATA_DIR = Path(__file__).parent
with open(_DATA_DIR / "disease_info.json") as f:
    _disease_data = json.load(f)

DISEASE_INFO = _disease_data["diseases"]
SEVERITY_COLOR = _disease_data["severity_colors"]


class CropDiseasePredictor:
    def __init__(self, model_path: str, class_names_path: str):
        print(f"Loading model from {model_path}...")
        
        # Load class names
        with open(class_names_path) as f:
            self.class_names = json.load(f)

        # Detect model type
        if model_path.endswith('.h5') or os.path.isfile(model_path):
            try:
                self.model = tf.keras.models.load_model(model_path)
                self._is_h5 = True
                print(f"H5 Model loaded | {len(self.class_names)} classes")
            except Exception as e:
                # Fallback: maybe it's a SavedModel file (less common)
                self.model = tf.saved_model.load(model_path)
                self._serve = self.model.signatures["serving_default"]
                self._is_h5 = False
                print(f"SavedModel loaded | {len(self.class_names)} classes")
        else:
            self.model = tf.saved_model.load(model_path)
            self._serve = self.model.signatures["serving_default"]
            self._is_h5 = False
            print(f"SavedModel loaded | {len(self.class_names)} classes")

    def predict_from_image(self, pil_image):
        """Predict disease from a PIL Image (used by the API)."""
        img = pil_image.convert("RGB").resize((224, 224))
        img_array = np.expand_dims(np.array(img, dtype=np.float32) / 255.0, axis=0)
        return self._run_prediction(img_array)

    def predict(self, img_path: str):
        """Predict disease from a file path (used for CLI testing)."""
        from PIL import Image
        img = Image.open(img_path).convert("RGB").resize((224, 224))
        img_array = np.expand_dims(np.array(img, dtype=np.float32) / 255.0, axis=0)
        return self._run_prediction(img_array)

    def _run_prediction(self, img_array):
        """Core prediction logic shared by both entry points."""
        if self._is_h5:
            predictions = self.model.predict(img_array, verbose=0)
        else:
            output = self._serve(tf.constant(img_array))
            # Get the first (and only) output tensor from the signature
            output_key = list(output.keys())[0]
            predictions = output[output_key].numpy()
        
        top5_indices = np.argsort(predictions[0])[-5:][::-1]
        top5 = [
            {"class": self.class_names[str(i)], "confidence": float(predictions[0][i])}
            for i in top5_indices
        ]

        best = top5[0]
        class_key = best["class"]
        info = DISEASE_INFO.get(class_key, {
            "display_name": class_key.replace("___", " - ").replace("_", " "),
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


if __name__ == "__main__":
    predictor = CropDiseasePredictor(config.MODEL_PATH, config.CLASS_NAMES_PATH)
    result = predictor.predict("test_leaf.jpg")
    print(f"\n {result['display_name']} | {result['confidence']}% | {result['severity']}")
