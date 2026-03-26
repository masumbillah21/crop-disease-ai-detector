# Project Proposal: CropScan AI

## 1. Problem Statement
Global agriculture faces a significant threat from crop diseases, which are responsible for an estimated 20–40% loss in global crop yields annually. For small-scale farmers, early and accurate identification of these diseases is often challenging due to a lack of access to agricultural experts or expensive diagnostic tools. Misdiagnosis leads to incorrect treatment, wasted resources, and further crop loss, impacting both food security and rural livelihoods.

## 2. Proposed Solution
**CropScan AI** is an end-to-end, AI-powered web application designed to provide instant, accessible, and accurate crop disease diagnosis. By simply uploading a photo of a plant leaf, users receive a detailed diagnosis, severity assessment, and actionable treatment recommendations. For large-scale monitoring, the platform includes an analytics dashboard to track disease prevalence and severity over time.

### Key Features:
- **Instant Diagnosis**: Real-time identification of 38 plant/disease classes.
- **Severity Assessment**: Categorization into Healthy, Moderate, High, or Critical risk.
- **Treatment & Prevention**: Tailored advice for managing and preventing identified diseases.
- **Analytics Dashboard**: Visual overview of scan history and disease trends.
- **Fully Dockerized**: Seamless deployment and environment consistency.

## 3. AI Approach
The core of CropScan AI is a Convolutional Neural Network (CNN) based on the **MobileNetV2** architecture.

- **Model Choice**: MobileNetV2 was selected for its high efficiency and low latency, making it ideal for deployment in resource-constrained environments (like mobile-friendly web apps) without sacrificing significant accuracy.
- **Transfer Learning**: The model uses pre-trained weights from ImageNet and is fine-tuned on the **PlantVillage Dataset**, which consists of over 54,000 images across 38 classes (apple, corn, potato, tomato, etc.).
- **Optimization**: The model is trained using the Adam optimizer and Sparse Categorical Crossentropy loss. Data augmentation (rotation, zoom, flips) is applied during training to improve generalization to real-world photos.

## 4. Tech Stack
CropScan AI utilizes a modern, robust tech stack designed for scalability and ease of use:

| Layer | Technology |
| :--- | :--- |
| **Frontend** | React 18, Vite, Recharts (for analytics), Tailwind CSS principles |
| **Backend** | FastAPI (Python 3.11), Uvicorn |
| **Machine Learning** | TensorFlow 2.15, Pillow (image processing) |
| **DevOps** | Docker, Docker Compose, Nginx (reverse proxy) |
| **Deployment** | Scalable to any Cloud Provider (AWS, GCP, Render, etc.) |
