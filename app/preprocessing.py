import io
import numpy as np
import tensorflow as tf
from PIL import Image

from app.model import get_model, get_input_shape

IMAGE_SIZE = (224, 224)


def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Preprocess image bytes for model prediction.

    Args:
        image_bytes: Raw image bytes from uploaded file

    Returns:
        Preprocessed image tensor ready for prediction
    """
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    img_array = np.array(image, dtype=np.float32)

    model = get_model()
    input_shape = get_input_shape(model)

    img_resized = tf.image.resize(img_array, input_shape)

    img_normalized = img_resized / 255.0

    img_batch = tf.expand_dims(img_normalized, axis=0)

    return img_batch.numpy()


def preprocess_image_for_display(image_bytes: bytes) -> np.ndarray:
    """
    Preprocess image for display (without normalization).

    Args:
        image_bytes: Raw image bytes from uploaded file

    Returns:
        Resized image as uint8 array
    """
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    img_array = np.array(image, dtype=np.float32)

    model = get_model()
    input_shape = get_input_shape(model)

    img_resized = tf.image.resize(img_array, input_shape)

    return img_resized.numpy().astype(np.uint8)
