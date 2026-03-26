# Final Project Report: CropScan AI

## 1. Executive Summary
**CropScan AI** is an advanced agricultural diagnostic system designed to bridge the gap between complex machine learning models and end-user accessibility. By utilizing a Dockerized microservices architecture, the project provides a seamless experience for detecting 38 different plant diseases through a high-performance web interface.

## 2. Problem Statement & Scope
Crop diseases result in billions of dollars in annual agricultural losses. The scope of this project was to develop a full-stack solution that allows:
- **Instant Diagnosis**: Identification of diseases across 14 species.
- **Actionable Insights**: Providing treatment and prevention steps.
- **Data Visualization**: Monitoring historical scan data for patterns.

## 3. Design Decisions

### Microservices with Docker
We chose to containerize the frontend (React/Nginx) and backend (FastAPI) separately to ensure environment consistency and scalability. Docker Compose orchestrates these services, allowing for a single-command setup.

### Backend: FastAPI
FastAPI was selected for its asynchronous capabilities and automatic OpenAPI documentation. It serves as a high-speed bridge between the React frontend and the TensorFlow inference engine. Environment variables and file paths are dynamically loaded through a centralized `config.py` using `python-dotenv`, enabling seamless transitions between local and cloud deployments.

### Frontend: React & Recharts
The UI prioritizes a "premium" user experience with a dark-theme dashboard. Recharts was used to provide real-time analytics, showing severity breakdowns and scan trends, which are crucial for long-term monitoring.

### AI Model: MobileNetV2
For the AI component, we implemented **MobileNetV2** due to its optimal balance of speed and accuracy. This allows the model to run efficiently even on servers with limited resources, providing near-instant results (sub-500ms inference time).

## 4. AI Workflow
The AI pipeline consists of:
1. **Data Ingestion**: Standardizing various image formats and sizes.
2. **Preprocessing**: Normalization and resizing to 224x224.
3. **Inference**: Prediction via the trained TensorFlow model.
4. **Post-processing**: Mapping class indices to human-readable names, severity levels, and treatment steps stored in a disease database.

## 5. Results & Validation
- **Accuracy**: The model achieved high validation accuracy on the PlantVillage dataset (~90%+).
- **Latency**: End-to-end processing (upload to result) is consistently under 1 second.
- **Usability**: Testing confirmed that the dashboard effectively visualizes mock and real scan data, providing clear value to the user.

## 6. Conclusion & Future Work
CropScan AI successfully demonstrates how AI can be democratized for agricultural use. Future iterations could include:
- **Offline Support**: Progress Web App (PWA) capabilities for field use.
- **GPS Tagging**: Mapping disease outbreaks geographically.
- **Multilingual Support**: Extending reach to global non-English speaking farming communities.

---
**Date**: March 25, 2026
**Version**: 1.0.0
