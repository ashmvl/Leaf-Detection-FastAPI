# Plant Disease Detection API with Grad-CAM

A FastAPI-based web application for detecting plant diseases from leaf images using deep learning, with integrated Grad-CAM and Grad-CAM++ visualizations to explain model predictions.

## Features

- **Disease Detection**: Classify plant diseases across 38 different categories
- **Grad-CAM Visualization**: Standard gradient-based class activation mapping
- **Grad-CAM++ Visualization**: Enhanced visualization with better localization
- **Web Interface**: User-friendly frontend for image upload and visualization
- **REST API**: Complete API for integration with n8n or other services
- **Docker Support**: Ready for deployment on DigitalOcean

## Project Structure

```
lead_api_2/
├── app/
│   ├── main.py              # FastAPI application and endpoints
│   ├── model.py             # Model loading and utilities
│   ├── preprocessing.py     # Image preprocessing
│   └── gradcam.py          # Grad-CAM implementations
├── static/
│   └── index.html          # Web interface
├── models/
│   └── best_model.keras    # Trained Keras model
├── tests/
│   └── test_api.py         # API tests
├── Dockerfile              # Docker configuration
├── .dockerignore          # Docker ignore file
├── requirements.txt       # Python dependencies
└── test_manual.py         # Manual testing script
```

## Supported Plant Classes

The model can detect 38 different plant disease categories including:
- Apple (scab, black rot, cedar rust, healthy)
- Corn (cercospora, rust, blight, healthy)
- Grape (black rot, esca, leaf blight, healthy)
- Tomato (bacterial spot, early/late blight, leaf mold, etc.)
- And many more...

## Installation

### Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd lead_api_2
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Ensure your model file exists at `models/best_model.keras`

5. Run the application:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

6. Open your browser and visit:
   - Web Interface: http://localhost:8080/static/index.html
   - API Documentation: http://localhost:8080/docs

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t plant-disease-api .
```

2. Run the container:
```bash
docker run -p 8080:8080 plant-disease-api
```

### DigitalOcean Deployment

1. **Create a DigitalOcean App**:
   - Go to DigitalOcean Apps
   - Create New App
   - Connect your Git repository

2. **Configure the App**:
   - Dockerfile: Use the included Dockerfile
   - Port: 8080
   - Health Check: `/health`

3. **Environment Variables** (optional):
   - `MODEL_PATH`: Path to the model file (default: `models/best_model.keras`)

4. **Deploy**:
   - Click "Deploy"
   - Wait for the build to complete
   - Your app will be available at the provided URL

## API Usage

### Health Check

```bash
GET /health
```

Response:
```json
{
  "status": "ok"
}
```

### Prediction Endpoint

```bash
POST /predict
```

**Parameters**:
- `file` (required): Image file (JPEG or PNG)
- `gradcam` (optional): Boolean - Request Grad-CAM visualization
- `gradcam_plus_plus` (optional): Boolean - Request Grad-CAM++ visualization

**Example with cURL**:

```bash
# Basic prediction
curl -X POST http://localhost:8080/predict \
  -F "file=@/path/to/leaf.jpg"

# With Grad-CAM visualization
curl -X POST http://localhost:8080/predict \
  -F "file=@/path/to/leaf.jpg" \
  -F "gradcam=true"

# With Grad-CAM++ visualization
curl -X POST http://localhost:8080/predict \
  -F "file=@/path/to/leaf.jpg" \
  -F "gradcam_plus_plus=true"
```

**Response**:

```json
{
  "label": "Tomato___Early_blight",
  "confidence": 0.95,
  "class_index": 29,
  "all_predictions": {
    "Apple___Apple_scab": 0.001,
    "Tomato___Early_blight": 0.95,
    ...
  },
  "gradcam": "base64_encoded_image_string"
}
```

### Python Example

```python
import requests

# Make prediction
with open("leaf.jpg", "rb") as f:
    files = {"file": f}
    data = {"gradcam": "true"}
    response = requests.post("http://localhost:8080/predict",
                           files=files, data=data)

result = response.json()
print(f"Disease: {result['label']}")
print(f"Confidence: {result['confidence']:.2%}")
```

## n8n Integration

To integrate with n8n:

1. Add an **HTTP Request Node**
2. Configure:
   - Method: POST
   - URL: `https://your-app.ondigitalocean.app/predict`
   - Body Content Type: Form-Data
   - Add field: `file` (binary data)
   - Add field: `gradcam` (true/false)
   - Add field: `gradcam_plus_plus` (true/false)
3. Parse the JSON response in subsequent nodes

## Testing

### Automated Tests

Run the test suite:

```bash
# Install test dependencies
pip install pytest httpx

# Run tests
pytest tests/ -v
```

### Manual Testing

Use the included test script:

```bash
python test_manual.py path/to/image.jpg --gradcam --gradcam-plus-plus
```

This will:
- Send the image to the API
- Display prediction results
- Save visualization images to disk

## Web Interface

Access the web interface at `/static/index.html`:

1. Upload an image by clicking or drag-and-drop
2. Select visualization options (Grad-CAM, Grad-CAM++)
3. Click "Analyze Image"
4. View results and visualizations

## Technical Details

### Model Architecture

- Base: Keras/TensorFlow model
- Input size: 224x224 RGB
- Output: 38 classes
- Preprocessing: Resize → Normalize (0-1 range)

### Grad-CAM

Visualizes important regions in the image for the model's decision:
- Uses gradients of the predicted class with respect to feature maps
- Highlights areas the model focuses on

### Grad-CAM++

Enhanced version with:
- Better localization using second-order gradients
- Improved visualization quality
- Better handling of multiple instances

## Performance Optimization

- Model is loaded once and cached in memory
- Headless OpenCV for reduced dependencies
- Non-root user in Docker for security
- Health checks for reliability

## Troubleshooting

### Model Loading Issues

If the model fails to load:
- Verify the model file exists at `models/best_model.keras`
- Check TensorFlow version compatibility
- Set `MODEL_PATH` environment variable if using a different location

### Memory Issues

If you encounter memory issues:
- Ensure sufficient RAM (recommended: 2GB+)
- Consider using a smaller TensorFlow build
- Optimize image sizes before upload

### Docker Build Issues

If Docker build fails:
- Ensure sufficient disk space
- Check that all required files are present
- Review .dockerignore to ensure model file is not excluded

## License

This project is provided as-is for educational and commercial use.

## Support

For issues and questions, please create an issue in the repository.
