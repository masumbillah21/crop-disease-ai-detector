# AI Model Methodology: CropScan AI

This document provides a detailed overview of the machine learning model, dataset, and training methodology used for the CropScan AI system.

## 1. Model Architecture
The system utilizes **MobileNetV2**, a streamlined and efficient convolutional neural network (CNN) architecture designed for mobile and embedded vision applications.

- **Base Model**: MobileNetV2 (Pre-trained on ImageNet).
- **Custom Top Layers**:
    - Global Average Pooling (to reduce spatial dimensions).
    - Batch Normalization (for training stability).
    - Dense Layer (512 units, ReLU activation).
    - Dropout (0.4) for regularization.
    - Dense Layer (256 units, ReLU activation).
    - Dropout (0.3).
    - Output Layer (38 units, Softmax activation).

## 2. Dataset
The model was trained on the **PlantVillage Dataset**, a publicly available collection of healthy and diseased leaf images.

- **Total Classes**: 38 (covering 14 plant species).
- **Total Images**: ~54,303.
- **Plants Included**: Apple, Blueberry, Cherry, Corn, Grape, Orange, Peach, Pepper, Potato, Raspberry, Soybean, Squash, Strawberry, Tomato.
- **Preprocessing**: All images were resized to **224x224** pixels and normalized to a [0, 1] range.

## 3. Training Strategy
We employed a two-phase transfer learning strategy to optimize performance while leveraging pre-trained features.

### Phase 1: Feature Extraction (10 Epochs)
- **Status**: Base model layers are frozen.
- **Optimizer**: Adam (Learning Rate: 0.001).
- **Goal**: Train the custom top layers to adapt to the 38-class plant disease task.

### Phase 2: Fine-Tuning (20 Epochs)
- **Status**: Last 30 layers of MobileNetV2 are unfrozen.
- **Optimizer**: Adam (Learning Rate: 0.0001).
- **Goal**: Fine-tune the deeper convolutional filters to better capture specific textures of plant diseases.

## 4. Training Parameters & Callbacks
- **Loss Function**: Categorical Crossentropy.
- **Metrics**: Accuracy.
- **Batch Size**: 32.
- **Data Augmentation**: Rotation (30°), Zoom (0.2), Horizontal Flip, Width/Height Shift (0.2).
- **Early Stopping**: Monitor validation loss with a patience of 5 epochs.
- **Learning Rate Scheduler**: `ReduceLROnPlateau` (Reduce factor: 0.3, Patience: 3 epochs).

## 5. Performance
The dual-phase training approach ensures high accuracy across various lighting conditions and orientations found in real-world leaf photography. Training history (accuracy/loss plots) is generated to verify convergence and prevent overfitting.

---
**Model Path**: `backend/model/crop_disease_model.h5`
**Class Names**: `backend/model/class_names.json`
