"""
Crop Disease Detection - Model Training Script
Dataset: PlantVillage (https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset)
Model: MobileNetV2 Transfer Learning
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
import matplotlib.pyplot as plt
import json

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 20
DATASET_DIR = "./dataset/plantvillage"  # Update this path
MODEL_SAVE_PATH = "./crop_disease_model.h5"
CLASS_NAMES_PATH = "./class_names.json"

# ─────────────────────────────────────────
# DATA GENERATORS
# ─────────────────────────────────────────
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=30,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    vertical_flip=False,
    fill_mode='nearest',
    validation_split=0.2
)

val_datagen = ImageDataGenerator(
    rescale=1./255,
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

print(f"✅ Found {len(class_names)} classes")
print(f"✅ Training samples: {train_generator.samples}")
print(f"✅ Validation samples: {val_generator.samples}")

# ─────────────────────────────────────────
# BUILD MODEL (Transfer Learning)
# ─────────────────────────────────────────
base_model = MobileNetV2(
    input_shape=(*IMG_SIZE, 3),
    include_top=False,
    weights='imagenet'
)
base_model.trainable = False  # Freeze base layers

model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.BatchNormalization(),
    layers.Dense(512, activation='relu'),
    layers.Dropout(0.4),
    layers.Dense(256, activation='relu'),
    layers.Dropout(0.3),
    layers.Dense(len(class_names), activation='softmax')
])

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
print("\n📌 Phase 1: Training top layers...")
history1 = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=10,
    callbacks=callbacks
)

# ─────────────────────────────────────────
# PHASE 2: Fine-tune last 30 layers
# ─────────────────────────────────────────
print("\n📌 Phase 2: Fine-tuning last 30 layers...")
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
    callbacks=callbacks
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
    print("✅ Training history saved to training_history.png")

plot_history(history1, history2)
print(f"\n✅ Model saved to: {MODEL_SAVE_PATH}")
print(f"✅ Class names saved to: {CLASS_NAMES_PATH}")
