# Quick Start Guide

Get your Plant Disease Detection API running in minutes!

## Prerequisites

- Python 3.10 or higher
- Model file at `models/best_model.keras`
- (Optional) Docker for containerized deployment

## Option 1: Quick Start with Scripts

### Linux/Mac

```bash
# Make the script executable
chmod +x start.sh

# Run the server
./start.sh
```

### Windows

```cmd
# Simply double-click start.bat or run:
start.bat
```

The script will:
1. Create a virtual environment (if needed)
2. Install dependencies
3. Start the server on http://localhost:8080

## Option 2: Manual Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

## Option 3: Docker

### Build and Run

```bash
# Build the image
docker build -t plant-disease-api .

# Run the container
docker run -p 8080:8080 plant-disease-api
```

### Or use Docker Compose

```bash
docker-compose up
```

## Access the Application

Once started, access:

- **Web Interface**: http://localhost:8080/static/index.html
- **API Documentation**: http://localhost:8080/docs
- **Health Check**: http://localhost:8080/health

## Testing the API

### Using the Web Interface

1. Open http://localhost:8080/static/index.html
2. Upload a plant leaf image
3. Select Grad-CAM or Grad-CAM++ visualization
4. Click "Analyze Image"
5. View results and visualizations

### Using cURL

```bash
# Basic prediction
curl -X POST http://localhost:8080/predict \
  -F "file=@path/to/leaf.jpg"

# With Grad-CAM
curl -X POST http://localhost:8080/predict \
  -F "file=@path/to/leaf.jpg" \
  -F "gradcam=true"

# With Grad-CAM++
curl -X POST http://localhost:8080/predict \
  -F "file=@path/to/leaf.jpg" \
  -F "gradcam_plus_plus=true"
```

### Using Python Test Script

```bash
python test_manual.py path/to/image.jpg --gradcam --gradcam-plus-plus
```

This will:
- Make a prediction
- Show results in terminal
- Save visualizations to disk

### Using Python Requests

```python
import requests

with open("leaf.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8080/predict",
        files={"file": f},
        data={"gradcam": "true"}
    )

print(response.json())
```

## Troubleshooting

### Issue: ModuleNotFoundError

**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: Model file not found

**Solution**: Ensure your model is at `models/best_model.keras`
```bash
ls models/best_model.keras
```

### Issue: Port 8080 already in use

**Solution**: Use a different port
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Issue: CUDA/GPU errors

**Solution**: This app uses CPU by default. If you have GPU issues:
```bash
export CUDA_VISIBLE_DEVICES=-1
```

## Next Steps

1. **Customize the model**: Replace `models/best_model.keras` with your trained model
2. **Update class names**: Edit `CLASS_NAMES` in `app/main.py`
3. **Deploy to production**: See DEPLOYMENT.md for DigitalOcean instructions
4. **Integrate with n8n**: Use the `/predict` endpoint in your n8n workflows

## API Endpoints Reference

### GET /health
Health check endpoint

**Response:**
```json
{
  "status": "ok"
}
```

### POST /predict
Make a prediction on an uploaded image

**Parameters:**
- `file` (required): Image file (JPEG/PNG)
- `gradcam` (optional): boolean - Request Grad-CAM visualization
- `gradcam_plus_plus` (optional): boolean - Request Grad-CAM++ visualization

**Response:**
```json
{
  "label": "Tomato___Early_blight",
  "confidence": 0.95,
  "class_index": 29,
  "all_predictions": {...},
  "gradcam": "base64_string_if_requested"
}
```

## Performance Tips

1. **Reduce image size**: Images are resized to 224x224, so upload appropriately sized images
2. **Disable reload**: Remove `--reload` flag in production
3. **Use Docker**: Containerized deployment is more efficient
4. **Enable caching**: Model is automatically cached after first load

## Support

- **Documentation**: See README.md for detailed documentation
- **Deployment**: See DEPLOYMENT.md for production deployment
- **Issues**: Create an issue in the repository

## Quick Commands Cheat Sheet

```bash
# Start server (development)
uvicorn app.main:app --reload

# Start server (production)
uvicorn app.main:app --host 0.0.0.0 --port 8080

# Run tests
pytest tests/ -v

# Build Docker image
docker build -t plant-disease-api .

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop Docker
docker-compose down
```

Happy plant disease detecting!
