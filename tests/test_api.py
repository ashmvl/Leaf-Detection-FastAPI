import io
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient
from PIL import Image
import numpy as np

from app.main import app

client = TestClient(app)


def create_test_image(size=(224, 224), format="PNG"):
    """Create a dummy test image."""
    img = Image.new("RGB", size, color=(73, 109, 137))
    img_bytes = io.BytesIO()
    img.save(img_bytes, format=format)
    img_bytes.seek(0)
    return img_bytes


class TestHealthEndpoint:
    """Test the health check endpoint."""

    def test_health_check(self):
        """Test that health endpoint returns OK status."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestRootEndpoint:
    """Test the root endpoint."""

    def test_root(self):
        """Test that root endpoint returns welcome message."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "docs" in data


class TestPredictEndpoint:
    """Test the prediction endpoint."""

    def test_predict_without_gradcam(self):
        """Test basic prediction without visualization."""
        img_bytes = create_test_image()
        files = {"file": ("test.png", img_bytes, "image/png")}

        response = client.post("/predict", files=files)

        assert response.status_code == 200
        data = response.json()

        assert "label" in data
        assert "confidence" in data
        assert "class_index" in data
        assert "all_predictions" in data

        assert isinstance(data["confidence"], float)
        assert 0 <= data["confidence"] <= 1
        assert isinstance(data["class_index"], int)

    def test_predict_with_gradcam(self):
        """Test prediction with Grad-CAM visualization."""
        img_bytes = create_test_image()
        files = {"file": ("test.png", img_bytes, "image/png")}
        data = {"gradcam": "true"}

        response = client.post("/predict", files=files, data=data)

        assert response.status_code == 200
        result = response.json()

        assert "label" in result
        assert "confidence" in result
        assert "gradcam" in result
        assert isinstance(result["gradcam"], str)
        assert len(result["gradcam"]) > 0

    def test_predict_with_gradcam_plus_plus(self):
        """Test prediction with Grad-CAM++ visualization."""
        img_bytes = create_test_image()
        files = {"file": ("test.png", img_bytes, "image/png")}
        data = {"gradcam_plus_plus": "true"}

        response = client.post("/predict", files=files, data=data)

        assert response.status_code == 200
        result = response.json()

        assert "label" in result
        assert "confidence" in result
        assert "gradcam++" in result
        assert isinstance(result["gradcam++"], str)
        assert len(result["gradcam++"]) > 0

    def test_predict_with_both_visualizations(self):
        """Test prediction with both Grad-CAM and Grad-CAM++."""
        img_bytes = create_test_image()
        files = {"file": ("test.png", img_bytes, "image/png")}
        data = {"gradcam": "true", "gradcam_plus_plus": "true"}

        response = client.post("/predict", files=files, data=data)

        assert response.status_code == 200
        result = response.json()

        assert "gradcam++" in result
        assert not ("gradcam" in result and "gradcam++" in result)

    def test_predict_jpeg_image(self):
        """Test prediction with JPEG image."""
        img_bytes = create_test_image(format="JPEG")
        files = {"file": ("test.jpg", img_bytes, "image/jpeg")}

        response = client.post("/predict", files=files)

        assert response.status_code == 200
        data = response.json()
        assert "label" in data
        assert "confidence" in data

    def test_predict_invalid_file_type(self):
        """Test that invalid file types are rejected."""
        txt_content = b"This is not an image"
        files = {"file": ("test.txt", io.BytesIO(txt_content), "text/plain")}

        response = client.post("/predict", files=files)

        assert response.status_code == 400
        assert "Invalid image type" in response.json()["detail"]

    def test_predict_without_file(self):
        """Test that request without file is rejected."""
        response = client.post("/predict")

        assert response.status_code == 422


class TestClassNames:
    """Test class names configuration."""

    def test_class_names_count(self):
        """Verify the number of classes matches expected."""
        from app.main import CLASS_NAMES

        assert len(CLASS_NAMES) == 38


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
