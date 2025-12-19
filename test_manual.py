#!/usr/bin/env python3
"""
Manual test script for the Plant Disease API.
This script allows you to test the API with a real image file.

Usage:
    python test_manual.py <image_path> [--gradcam] [--gradcam-plus-plus]

Example:
    python test_manual.py test_leaf.jpg --gradcam
"""

import argparse
import requests
import base64
from pathlib import Path


def test_api(image_path: str, base_url: str = "http://localhost:8080",
             gradcam: bool = False, gradcam_plus_plus: bool = False):
    """
    Test the API with a given image.

    Args:
        image_path: Path to the image file
        base_url: Base URL of the API
        gradcam: Whether to request Grad-CAM visualization
        gradcam_plus_plus: Whether to request Grad-CAM++ visualization
    """
    # Check if file exists
    if not Path(image_path).exists():
        print(f"Error: File not found: {image_path}")
        return

    print(f"Testing API with image: {image_path}")
    print(f"Base URL: {base_url}")
    print(f"Grad-CAM: {gradcam}")
    print(f"Grad-CAM++: {gradcam_plus_plus}")
    print("-" * 50)

    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health check: {response.json()}")
    except Exception as e:
        print(f"Error checking health: {e}")
        return

    # Test prediction endpoint
    try:
        with open(image_path, "rb") as f:
            files = {"file": f}
            data = {
                "gradcam": str(gradcam).lower(),
                "gradcam_plus_plus": str(gradcam_plus_plus).lower()
            }

            response = requests.post(f"{base_url}/predict", files=files, data=data)
            response.raise_for_status()

            result = response.json()

            print("\nPrediction Results:")
            print(f"Label: {result['label']}")
            print(f"Confidence: {result['confidence']:.2%}")
            print(f"Class Index: {result['class_index']}")

            if gradcam and "gradcam" in result:
                print("\nGrad-CAM visualization received")
                print(f"Base64 length: {len(result['gradcam'])} characters")

                # Optionally save the visualization
                output_path = Path(image_path).stem + "_gradcam.png"
                with open(output_path, "wb") as out:
                    out.write(base64.b64decode(result["gradcam"]))
                print(f"Saved visualization to: {output_path}")

            if gradcam_plus_plus and "gradcam++" in result:
                print("\nGrad-CAM++ visualization received")
                print(f"Base64 length: {len(result['gradcam++'])} characters")

                # Optionally save the visualization
                output_path = Path(image_path).stem + "_gradcam_plus_plus.png"
                with open(output_path, "wb") as out:
                    out.write(base64.b64decode(result["gradcam++"]))
                print(f"Saved visualization to: {output_path}")

            print("\nTop 5 predictions:")
            sorted_preds = sorted(
                result["all_predictions"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            for label, conf in sorted_preds:
                print(f"  {label}: {conf:.2%}")

    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the Plant Disease API")
    parser.add_argument("image_path", help="Path to the image file")
    parser.add_argument("--base-url", default="http://localhost:8080",
                        help="Base URL of the API (default: http://localhost:8080)")
    parser.add_argument("--gradcam", action="store_true",
                        help="Request Grad-CAM visualization")
    parser.add_argument("--gradcam-plus-plus", action="store_true",
                        help="Request Grad-CAM++ visualization")

    args = parser.parse_args()

    test_api(args.image_path, args.base_url, args.gradcam, args.gradcam_plus_plus)
