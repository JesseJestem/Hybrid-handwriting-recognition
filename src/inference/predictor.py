from pathlib import Path
import sys
import numpy as np
import tensorflow as tf

#~~~~~~~~~~~~~~~~~~~~~~~~
#path
#~~~~~~~~~~~~~~~~~~~~~~~~

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(BASE_DIR))

#import project preprocess defs
from src.preprocessing.image_preprocessing import preprocess_image
from handwriting.preprocessing.strokes import preprocess_strokes

#models paths
MODEL_PATH = BASE_DIR / "saved_models" / "hybrid_letters.keras"
DATASET_PATH = BASE_DIR / "data" / "processed" / "dataset.npz"

#global variabels
_model = None
_display_labels = None

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#loading resources for model prediction
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def load_prediction_resources():
    #global variabels loading for the first time and reuse it
    global _model, _display_labels

    #checking and loading model
    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model not found: {MODEL_PATH}")

        _model = tf.keras.models.load_model(MODEL_PATH, compile=False)

    #checking and loading labels
    if _display_labels is None:
        if not DATASET_PATH.exists():
            raise FileNotFoundError(f"Dataset not found: {DATASET_PATH}")

        data = np.load(DATASET_PATH, allow_pickle=True)
        _display_labels = data["display_labels"]

    return _model, _display_labels

#~~~~~~~~~~~~~~~~~~~~~
#main predict function
#~~~~~~~~~~~~~~~~~~~~~

def predict_from_files(
    image_path: str | Path, #input img path
    stroke_path: str | Path, #input stroke path
    top_k: int = 3, #show 3 best predictions
) -> dict:

    model, display_labels = load_prediction_resources()

    #file preprocessing
    image_array = preprocess_image(image_path)
    stroke_array = preprocess_strokes(stroke_path)

    #add batch dimension:
    #(64, 64, 1) -> (1, 64, 64, 1)
    #(100, 5) -> (1, 100, 5)
    image_batch = np.expand_dims(image_array, axis=0) #add new dim in begining
    stroke_batch = np.expand_dims(stroke_array, axis=0) #add new dim in begining

    #prediction of model
    logits = model.predict(
        {
            "image_input": image_batch,
            "stroke_input": stroke_batch,
        },
        verbose=0, #print only result without 1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 120ms/step and ets
    )

    #turn logits to softmax, axis=1 use softmax to classes (1, 52), numpy() transform tf array to np, [0] (1, 52) -> (52,)
    probs = tf.nn.softmax(logits, axis=1).numpy()[0]

    #take top indicates np.argsort(probs)[::-1] - take sorted probs(min->max) and revers it, [:top_k] take 3 of them for display
    top_indices = np.argsort(probs)[::-1][:top_k]

    #add results from top classes
    top_results = []
    for index in top_indices:
        top_results.append(
            {
                "label": str(display_labels[index]),
                "confidence": float(probs[index]),
            }
        )

    return {
        "prediction": top_results[0]["label"],
        "confidence": top_results[0]["confidence"],
        "top_k": top_results,
    }