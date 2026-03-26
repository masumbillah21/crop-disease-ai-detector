import os
from dotenv import load_dotenv

# Load .env file natively
load_dotenv()

# Model and Data Paths
MODEL_PATH = os.getenv("MODEL_PATH", "/app/model/crop_disease_model")
CLASS_NAMES_PATH = os.getenv("CLASS_NAMES_PATH", "/app/model/class_names.json")
DATASET_DIR = os.getenv("DATASET_DIR", "./dataset/plantvillage/plantvillage dataset/color")
MODEL_SAVE_PATH = os.getenv("MODEL_SAVE_PATH", "./crop_disease_model.h5")

# Application Settings
PORT = int(os.getenv("PORT", 8000))
