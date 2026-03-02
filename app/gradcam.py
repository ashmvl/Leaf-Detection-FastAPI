import io
import base64
import numpy as np
import tensorflow as tf
import cv2
import matplotlib
matplotlib.use('Agg')
import matplotlib.cm as cm

from app.model import get_model, get_last_conv_layer_name
from app.preprocessing import preprocess_image, preprocess_image_for_display


def make_gradcam_heatmap(img_array: np.ndarray, model, last_conv_layer_name: str) -> np.ndarray:
    """
    Generate Grad-CAM heatmap for the given image.

    Args:
        img_array: Preprocessed image tensor (batch of 1)
        model: Keras model
        last_conv_layer_name: Name of the last convolutional layer

    Returns:
        Heatmap as numpy array
    """
    model_output = model.outputs[0] if isinstance(model.outputs, (list, tuple)) else model.outputs
    grad_model = tf.keras.models.Model(
        model.inputs, [model.get_layer(last_conv_layer_name).output, model_output]
    )

    with tf.GradientTape() as tape:
        model_inputs = [img_array] if isinstance(model.inputs, (list, tuple)) and len(model.inputs) == 1 else img_array
        last_conv_layer_output, predictions = grad_model(model_inputs)
        if isinstance(predictions, (list, tuple)):
            predictions = predictions[0]
        pred_index = tf.argmax(predictions[0])
        class_channel = predictions[:, pred_index]

    grads = tape.gradient(class_channel, last_conv_layer_output)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    last_conv_layer_output = last_conv_layer_output[0]
    heatmap = last_conv_layer_output @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)

    heatmap = tf.maximum(heatmap, 0) / (tf.reduce_max(heatmap) + 1e-8)
    return heatmap.numpy()


def make_gradcam_plus_plus_heatmap(img_array: np.ndarray, model, last_conv_layer_name: str) -> np.ndarray:
    """
    Generate Grad-CAM++ heatmap for the given image.

    Args:
        img_array: Preprocessed image tensor (batch of 1)
        model: Keras model
        last_conv_layer_name: Name of the last convolutional layer

    Returns:
        Heatmap as numpy array
    """
    model_output = model.outputs[0] if isinstance(model.outputs, (list, tuple)) else model.outputs
    grad_model = tf.keras.models.Model(
        model.inputs, [model.get_layer(last_conv_layer_name).output, model_output]
    )

    with tf.GradientTape(persistent=True) as tape:
        model_inputs = [img_array] if isinstance(model.inputs, (list, tuple)) and len(model.inputs) == 1 else img_array
        last_conv_layer_output, predictions = grad_model(model_inputs)
        if isinstance(predictions, (list, tuple)):
            predictions = predictions[0]
        pred_index = tf.argmax(predictions[0])
        class_channel = predictions[:, pred_index]

        grads = tape.gradient(class_channel, last_conv_layer_output)
        tape.gradient(grads, last_conv_layer_output)

    grads_squared = tf.square(grads)
    grads_cubed = tf.pow(grads, 3)

    epsilon = 1e-7
    denominator = 2 * grads_squared + last_conv_layer_output * grads_cubed + epsilon
    alpha_num = grads_squared
    alpha = alpha_num / denominator

    alpha_pooled = tf.reduce_sum(alpha, axis=(0, 1, 2))

    last_conv_layer_output = last_conv_layer_output[0]
    heatmap = last_conv_layer_output * alpha_pooled
    heatmap = tf.reduce_sum(heatmap, axis=-1)

    heatmap = tf.maximum(heatmap, 0) / (tf.reduce_max(heatmap) + 1e-8)
    return heatmap.numpy()


def create_superimposed_image(original_image: np.ndarray, heatmap: np.ndarray, alpha: float = 0.5) -> np.ndarray:
    """
    Superimpose heatmap on original image.

    Args:
        original_image: Original image as uint8 array
        heatmap: Grad-CAM heatmap
        alpha: Transparency factor for overlay

    Returns:
        Superimposed image as uint8 array (RGB)
    """
    heatmap = heatmap.astype(np.float32)

    heatmap_resized = cv2.resize(heatmap, (original_image.shape[1], original_image.shape[0]))

    heatmap_colored = np.uint8(255 * heatmap_resized)
    colormap = matplotlib.colormaps.get_cmap("jet")
    heatmap_colored = (colormap(heatmap_colored)[..., :3] * 255).astype(np.uint8)

    heatmap_colored_bgr = cv2.cvtColor(heatmap_colored, cv2.COLOR_RGB2BGR)
    original_image_bgr = cv2.cvtColor(original_image, cv2.COLOR_RGB2BGR)

    original_float = original_image_bgr.astype(np.float32)
    heatmap_float = heatmap_colored_bgr.astype(np.float32)

    superimposed = heatmap_float * alpha + original_float * (1 - alpha)
    superimposed = np.uint8(superimposed)

    superimposed_rgb = cv2.cvtColor(superimposed, cv2.COLOR_BGR2RGB)
    return superimposed_rgb


def image_to_base64(image: np.ndarray, format: str = "PNG") -> str:
    """
    Convert numpy image array to base64 string.

    Args:
        image: Image as numpy array (RGB)
        format: Output format (PNG or JPEG)

    Returns:
        Base64 encoded image string
    """
    from PIL import Image as PILImage

    pil_image = PILImage.fromarray(image)
    buffer = io.BytesIO()
    pil_image.save(buffer, format=format)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


def generate_gradcam(image_bytes: bytes, use_plus_plus: bool = False) -> str:
    """
    Generate Grad-CAM visualization and return as base64.

    Args:
        image_bytes: Raw image bytes
        use_plus_plus: If True, use Grad-CAM++ instead of Grad-CAM

    Returns:
        Base64 encoded superimposed image
    """
    model = get_model()
    last_conv_layer_name = get_last_conv_layer_name(model)

    img_tensor = preprocess_image(image_bytes)
    original_image = preprocess_image_for_display(image_bytes)

    if use_plus_plus:
        heatmap = make_gradcam_plus_plus_heatmap(img_tensor, model, last_conv_layer_name)
    else:
        heatmap = make_gradcam_heatmap(img_tensor, model, last_conv_layer_name)

    superimposed = create_superimposed_image(original_image, heatmap, alpha=0.5)

    return image_to_base64(superimposed)
