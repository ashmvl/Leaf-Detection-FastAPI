from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.model import get_model
from app.preprocessing import preprocess_image, preprocess_image_for_display
from app.gradcam import generate_gradcam, image_to_base64

import numpy as np

app = FastAPI(title="Leaf Disease API")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

CLASS_NAMES = [
    "Apple___Apple_scab", "Apple___Black_rot", "Apple___Cedar_apple_rust", "Apple___healthy",
    "Blueberry___healthy", "Cherry_(including_sour)___Powdery_mildew",
    "Cherry_(including_sour)___healthy", "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn_(maize)___Common_rust_", "Corn_(maize)___Northern_Leaf_Blight", "Corn_(maize)___healthy",
    "Grape___Black_rot", "Grape___Esca_(Black_Measles)", "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "Grape___healthy", "Orange___Haunglongbing_(Citrus_greening)", "Peach___Bacterial_spot",
    "Peach___healthy", "Pepper,_bell___Bacterial_spot", "Pepper,_bell___healthy",
    "Potato___Early_blight", "Potato___Late_blight", "Potato___healthy",
    "Raspberry___healthy", "Soybean___healthy", "Squash___Powdery_mildew",
    "Strawberry___Leaf_scorch", "Strawberry___healthy", "Tomato___Bacterial_spot",
    "Tomato___Early_blight", "Tomato___Late_blight", "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot", "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot", "Tomato___Tomato_Yellow_Leaf_Curl_Virus", "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy"
]

@app.get("/")
def root():
    return {"message": "Leaf Disease Classification API", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    gradcam: bool = Query(default=False),
    gradcam_plus_plus: bool = Query(default=False)
):
    """
    Predict plant disease from uploaded image.

    Args:
        file: Image file (JPEG or PNG)
        gradcam: Return standard Grad-CAM visualization
        gradcam_plus_plus: Return Grad-CAM++ visualization

    Returns:
        JSON with prediction, confidence, and optional visualization
    """
    if file.content_type not in ("image/jpeg", "image/png", "image/jpg"):
        raise HTTPException(status_code=400, detail="Invalid image type. Only JPEG and PNG are supported.")

    try:
        image_bytes = await file.read()
        image_tensor = preprocess_image(image_bytes)

        model = get_model()
        preds = model.predict(image_tensor)[0]
        idx = int(np.argmax(preds))

        response = {
            "label": CLASS_NAMES[idx],
            "confidence": float(preds[idx]),
            "class_index": idx,
            "all_predictions": {CLASS_NAMES[i]: float(preds[i]) for i in range(len(CLASS_NAMES))}
        }

        if gradcam or gradcam_plus_plus:
            response["original_image"] = image_to_base64(preprocess_image_for_display(image_bytes))

        if gradcam:
            heatmap_base64 = generate_gradcam(image_bytes, use_plus_plus=False)
            response["gradcam"] = heatmap_base64

        if gradcam_plus_plus:
            heatmap_base64_pp = generate_gradcam(image_bytes, use_plus_plus=True)
            response["gradcam_plus_plus"] = heatmap_base64_pp
            response["gradcam++"] = heatmap_base64_pp

        return JSONResponse(response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
