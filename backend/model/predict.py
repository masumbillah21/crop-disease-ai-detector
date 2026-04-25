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

        self._is_keras = False
        self._serve = None
        self.model = None

        # Strategy 1: Try tf.keras.models.load_model() first (works for .h5 AND SavedModel)
        # This is the most reliable path — uses model.predict() which preserves softmax output
        try:
            self.model = tf.keras.models.load_model(model_path)
            self._is_keras = True
            print(f"Keras model loaded | {len(self.class_names)} classes")
            return
        except Exception as e:
            print(f"Keras load failed for {model_path}: {e}")

        # Strategy 2: Try modern .keras or legacy .h5 fallback
        keras_path = model_path + ".keras" if not model_path.endswith(".keras") else model_path
        h5_path = model_path + ".h5" if not model_path.endswith(".h5") else model_path
        fallback_dir = os.path.dirname(model_path)
        
        candidates = [
            keras_path,
            h5_path,
            os.path.join(fallback_dir, "crop_disease_model.keras"),
            os.path.join(fallback_dir, "crop_disease_model.h5")
        ]

        for path in candidates:
            if os.path.isfile(path):
                try:
                    self.model = tf.keras.models.load_model(path)
                    self._is_keras = True
                    print(f"Model loaded from {path} | {len(self.class_names)} classes")
                    return
                except Exception as e:
                    print(f"Load failed for {path}: {e}")

        # Strategy 3: Last resort — tf.saved_model.load() for export()-style SavedModel
        if os.path.isdir(model_path):
            try:
                self.model = tf.saved_model.load(model_path)
                self._serve = self.model.signatures["serving_default"]
                self._is_keras = False
                print(f"SavedModel loaded (serving) | {len(self.class_names)} classes")
                return
            except Exception as e:
                print(f"SavedModel load failed: {e}")

        if self.model is None:
            raise RuntimeError(f"Could not load model from any source. Tried: {model_path}")

    def predict_from_image(self, pil_image):
        """Predict disease from a PIL Image (used by the API)."""
        img = pil_image.convert("RGB").resize((224, 224))
        # Use MobileNetV2 standard preprocessing: scale to [-1, 1]
        img_array = (np.array(img, dtype=np.float32) / 127.5) - 1.0
        img_array = np.expand_dims(img_array, axis=0)
        return self._run_prediction(img_array)

    def predict(self, img_path: str):
        """Predict disease from a file path (used for CLI testing)."""
        from PIL import Image
        img = Image.open(img_path).convert("RGB").resize((224, 224))
        # Use MobileNetV2 standard preprocessing: scale to [-1, 1]
        img_array = (np.array(img, dtype=np.float32) / 127.5) - 1.0
        img_array = np.expand_dims(img_array, axis=0)
        return self._run_prediction(img_array)

    def _run_prediction(self, img_array):
        """Core prediction logic shared by both entry points."""
        if self._is_keras:
            predictions = self.model.predict(img_array, verbose=0)
        else:
            output = self._serve(tf.constant(img_array))
            output_key = list(output.keys())[0]
            raw = output[output_key].numpy()
            # If the model was exported with model.export(), the output may be
            # logits instead of probabilities. Apply softmax if values aren't
            # already in the [0, 1] probability range summing to ~1.
            if raw.sum() < 0.99 or raw.sum() > 1.01 or raw.min() < 0:
                predictions = tf.nn.softmax(raw).numpy()
            else:
                predictions = raw
        
        top5_indices = np.argsort(predictions[0])[-5:][::-1]
        top5 = [
            {"class": self.class_names[str(i)], "confidence": float(predictions[0][i])}
            for i in top5_indices
        ]

        best = top5[0]
        confidence = round(best["confidence"] * 100, 2)
        
        # Apply Confidence Threshold (OOD detection)
        # If confidence is too low, we treat it as Unknown
        if confidence < 50.0:
            class_key = "Unknown"
        else:
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
            "confidence": confidence,
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
