import os
import tensorflow as tf
from tensorflow import keras

MODEL_PATH = os.environ.get("MODEL_PATH", "models/best_model.keras")

_model = None


def get_model():
    """Load and cache the Keras model."""
    global _model
    if _model is None:
        _model = tf.keras.models.load_model(MODEL_PATH)
    return _model


def get_last_conv_layer_name(model):
    """Find the last convolutional layer name in the model."""
    for layer in reversed(model.layers):
        if isinstance(layer, keras.layers.Conv2D):
            return layer.name
    raise ValueError("Could not find a convolutional layer in the model.")


def get_input_shape(model):
    """Get the expected input shape from the model."""
    return tuple(model.input_shape[1:3])  # Returns (height, width)
