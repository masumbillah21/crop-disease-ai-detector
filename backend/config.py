import os
from dotenv import load_dotenv

# Load .env file natively
load_dotenv()

# Absolute paths (consistent across local/Docker and different CWDs)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Model and Data Paths
MODEL_PATH = os.getenv("MODEL_PATH", os.path.join(BASE_DIR, "model", "crop_disease_model.keras"))
CLASS_NAMES_PATH = os.getenv("CLASS_NAMES_PATH", os.path.join(BASE_DIR, "model", "class_names.json"))

# Prefer merged dataset if it exists
merged_dataset_path = os.path.join(BASE_DIR, "model", "dataset", "merged_dataset")
default_dataset_dir = merged_dataset_path
DATASET_DIR = os.getenv("DATASET_DIR", default_dataset_dir)

MODEL_SAVE_PATH = os.getenv("MODEL_SAVE_PATH", os.path.join(BASE_DIR, "model", "crop_disease_model.keras"))

# Application Settings
PORT = int(os.getenv("PORT", 8000))
