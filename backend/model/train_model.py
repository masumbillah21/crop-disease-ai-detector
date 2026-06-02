"""
Crop Disease Detection - Model Training Script
Dataset: PlantVillage (https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset)
Model: MobileNetV2 Transfer Learning
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import EfficientNetV2B0
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
import matplotlib.pyplot as plt
import json
import sys
from pathlib import Path

# Add backend dir to sys.path for standalone execution
sys.path.append(str(Path(__file__).parent.parent))
import config

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
import argparse

parser = argparse.ArgumentParser(description="Train Crop Disease Detection Model")
parser.add_argument("--test", action="store_true", help="Run a quick 1-step test of the training pipeline")
args = parser.parse_args()

IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 1 if args.test else 20
DATASET_DIR = config.DATASET_DIR
MODEL_SAVE_PATH = config.MODEL_SAVE_PATH
SAVEDMODEL_PATH = config.MODEL_PATH
CLASS_NAMES_PATH = config.CLASS_NAMES_PATH

# Configure test run steps
fit_kwargs = {"steps_per_epoch": 2, "validation_steps": 1} if args.test else {}

# ─────────────────────────────────────────
# DATA GENERATORS
# ─────────────────────────────────────────
train_datagen = ImageDataGenerator(
    rotation_range=30,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    brightness_range=[0.8, 1.2],  # Simulates varied indoor/outdoor lighting conditions
    horizontal_flip=True,
    vertical_flip=False,
    fill_mode='nearest',
    validation_split=0.2
)

val_datagen = ImageDataGenerator(
    validation_split=0.2
)

train_generator = train_datagen.flow_from_directory(
    DATASET_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training',
    shuffle=True
)

val_generator = val_datagen.flow_from_directory(
    DATASET_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation',
    shuffle=False
)

# Save class names
class_names = {v: k for k, v in train_generator.class_indices.items()}
with open(CLASS_NAMES_PATH, 'w') as f:
    json.dump(class_names, f, indent=2)

print(f"Found {len(class_names)} classes")
print(f"Training samples: {train_generator.samples}")
print(f"Validation samples: {val_generator.samples}")

# Compute balanced class weights to handle severe class imbalance
from collections import Counter
class_counts = Counter(train_generator.classes)
total_samples = train_generator.samples
num_classes = len(class_names)

class_weights = {}
for cls_idx, count in class_counts.items():
    weight = total_samples / (num_classes * count)
    # Clip weights to prevent gradient explosions while maintaining class impact
    class_weights[cls_idx] = float(np.clip(weight, 0.2, 8.0))

print("\nComputed Class Weights (sample of first 5):")
for i in list(class_weights.keys())[:5]:
    print(f"  Class {i} ({class_names[i]}): count={class_counts[i]}, weight={class_weights[i]:.3f}")

# ─────────────────────────────────────────
# BUILD MODEL (Transfer Learning - Functional API)
# ─────────────────────────────────────────
base_model = EfficientNetV2B0(
    input_shape=(*IMG_SIZE, 3),
    include_top=False,
    weights='imagenet'
)
base_model.trainable = False  # Freeze base layers

inputs = tf.keras.Input(shape=(*IMG_SIZE, 3))
x = base_model(inputs, training=False)
x = layers.GlobalAveragePooling2D()(x)
x = layers.BatchNormalization()(x)
x = layers.Dense(512, activation='relu')(x)
x = layers.Dropout(0.4)(x)
x = layers.Dense(256, activation='relu')(x)
x = layers.Dropout(0.3)(x)
outputs = layers.Dense(len(class_names), activation='softmax')(x)

model = models.Model(inputs, outputs)

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

model.summary()

# ─────────────────────────────────────────
# CALLBACKS
# ─────────────────────────────────────────
callbacks = [
    ModelCheckpoint(
        MODEL_SAVE_PATH,
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1
    ),
    EarlyStopping(
        monitor='val_loss',
        patience=5,
        restore_best_weights=True,
        verbose=1
    ),
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.3,
        patience=3,
        min_lr=1e-6,
        verbose=1
    )
]

# ─────────────────────────────────────────
# PHASE 1: Train top layers only
# ─────────────────────────────────────────
print("\nPhase 1: Training top layers...")
history1 = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=1 if args.test else 10,
    class_weight=class_weights,
    callbacks=callbacks,
    **fit_kwargs
)

# ─────────────────────────────────────────
# PHASE 2: Fine-tune last 30 layers
# ─────────────────────────────────────────
print("\nPhase 2: Fine-tuning last 30 layers...")
base_model.trainable = True
for layer in base_model.layers[:-30]:
    layer.trainable = False

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

history2 = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=EPOCHS,
    class_weight=class_weights,
    callbacks=callbacks,
    **fit_kwargs
)

# ─────────────────────────────────────────
# PLOT TRAINING HISTORY
# ─────────────────────────────────────────
def plot_history(h1, h2):
    acc = h1.history['accuracy'] + h2.history['accuracy']
    val_acc = h1.history['val_accuracy'] + h2.history['val_accuracy']
    loss = h1.history['loss'] + h2.history['loss']
    val_loss = h1.history['val_loss'] + h2.history['val_loss']

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    axes[0].plot(acc, label='Train Accuracy', color='#2ecc71')
    axes[0].plot(val_acc, label='Val Accuracy', color='#3498db')
    axes[0].set_title('Model Accuracy')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(loss, label='Train Loss', color='#e74c3c')
    axes[1].plot(val_loss, label='Val Loss', color='#f39c12')
    axes[1].set_title('Model Loss')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('./training_history.png', dpi=150)
    print("Training history saved to training_history.png")

plot_history(history1, history2)

# Export as Keras format
model.save(SAVEDMODEL_PATH)
print(f"\nModel saved to: {MODEL_SAVE_PATH}")
print(f"SavedModel exported to: {SAVEDMODEL_PATH}")
print(f"Class names saved to: {CLASS_NAMES_PATH}")

