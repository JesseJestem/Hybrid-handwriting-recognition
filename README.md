# Hybrid Handwriting Recognition

## Project Overview

This project is a handwriting recognition system for handwritten input from a mouse, touchpad, touchscreen, or stylus.

The current MVP combines a data collection application with a trained hybrid neural network that uses image-based and stroke-based recognition.

The first target is recognition of uppercase and lowercase English letters:

```text
A-Z
a-z
```

In future versions, the project will be extended to support:

- digits
- special symbols
- other alphabets
- full word recognition

---

## Project Goal

The final goal is to create a neural network that can recognize handwritten text from touch or stylus input.

Unlike a simple image classifier, this project uses a hybrid approach:

```text
Handwritten image + stroke movement data → neural network → predicted character / word
```

This allows the model to learn not only the final shape of a character, but also how the character was written.

---

## Current Stage

The project is currently at the first working MVP stage.

The application allows the user to:

- select a character label
- draw a handwritten character on a canvas
- save the drawing as a PNG image
- save stroke coordinates as JSON data
- collect and extend a custom dataset
- predict a handwritten character with the trained hybrid model
- display prediction confidence and Top-3 results

---

## Why Hybrid Recognition?

There are two common ways to recognize handwriting.

### 1. Image-based recognition

The model receives only the final image.

Example:

```text
PNG image of letter "A" → model → "A"
```

This approach is simple and works well with CNN models.

### 2. Stroke-based recognition

The model receives the sequence of points created while writing.

Example:

```json
[
  { "x": 120, "y": 300, "t": 0 },
  { "x": 125, "y": 290, "t": 16 },
  { "x": 130, "y": 280, "t": 32 }
]
```

This approach allows the model to understand writing direction, speed, movement order, and pauses.

### 3. Hybrid approach

This project combines both approaches:

```text
Image input → CNN branch
Stroke input → LSTM / GRU / Transformer branch
Combined features → classifier
```

The hybrid model is expected to be stronger than using only images or only stroke data.

---

## Current Model Architecture

The current model classifies individual English letters.

```text
Input 1: 64x64 grayscale image
        ↓
        CNN branch
        ↓
        image features

Input 2: sequence of stroke points
        ↓
        LSTM / GRU branch
        ↓
        stroke features

image features + stroke features
        ↓
        Dense layers
        ↓
        Softmax
        ↓
        predicted character
```

Initial output classes:

```text
A-Z + a-z = 52 classes
```

---

## Data Format

Each sample consists of two files:

```text
1. PNG image
2. JSON stroke data
```

Example dataset structure:

```text
data/
└── raw/
    ├── images/
    │   ├── upper_A/
    │   ├── upper_B/
    │   ├── lower_a/
    │   └── lower_b/
    │
    └── strokes/
        ├── upper_A/
        ├── upper_B/
        ├── lower_a/
        └── lower_b/
```

Example JSON file:

```json
{
  "label": "A",
  "image_path": "C:\\Users....A_20260523_011849_558783.png",
  "canvas_width": 400,
  "canvas_height": 400,
  "strokes": [
    {
      "x": 120.5,
      "y": 330.1,
      "t": 0,
      "pressure": 0.5,
      "pen_down": true
    }
  ]
}
```

---

## Tech Stack

### Frontend

- HTML
- CSS
- JavaScript
- Canvas API
- Pointer Events API

### Backend

- Python
- FastAPI
- Uvicorn
- Pydantic

### Machine Learning Stack

- TensorFlow / Keras
- NumPy
- Pillow
- scikit-learn
- Matplotlib

---

## Features

### Implemented

- [x] Drawing canvas
- [x] Character label selection
- [x] PNG image export
- [x] FastAPI endpoint for saving samples
- [x] Dataset folder structure
- [x] JSON stroke export
- [x] Stroke coordinate collection
- [x] Support for uppercase English letters
- [x] Support for lowercase English letters
- [x] Dataset collection workflow
- [x] Image preprocessing
- [x] Stroke preprocessing
- [x] Dataset preprocessing script
- [x] Dataset builder
- [x] Hybrid model
- [x] Model training and evaluation
- [x] Classification report
- [x] Confusion matrix
- [x] Saved Keras model
- [x] Command-line prediction tool
- [x] FastAPI prediction endpoint
- [x] Prediction from the browser interface
- [x] Prediction confidence and Top-3 results
- [x] Temporary prediction file cleanup
- [x] Data augmentation
- [x] Expand and balance the dataset

### In Progress

- [ ] CNN image model
- [ ] Stroke-based sequence model
- [ ] Analyze incorrect predictions
- [ ] Improve model evaluation on new handwriting sessions and writers

### Planned

- [ ] Automated tests
- [ ] Model and dataset versioning
- [ ] Digits recognition
- [ ] Symbol recognition
- [ ] Other alphabets
- [ ] Word-level recognition

---

## Roadmap

### Phase 1: Data Collection App

Goal: collect handwritten English letters.

Target classes:

```text
A-Z
a-z
```

Tasks:

- [x] Create canvas interface
- [x] Collect stroke points
- [x] Save image data
- [x] Save stroke data
- [x] Improve UI
- [x] Add uppercase and lowercase label selector
- [x] Add sample counter
- [x] Add dataset statistics

---

### Phase 2: Dataset Preprocessing

Goal: convert raw data into training-ready arrays.

Tasks:

- [x] Load PNG images
- [x] Convert images to grayscale
- [x] Crop empty space
- [x] Resize images to 64x64
- [x] Normalize pixel values
- [x] Load JSON stroke data
- [x] Normalize coordinates
- [x] Normalize time values
- [x] Pad or resample stroke sequences
- [x] Build dataset
- [x] Save processed dataset as `.npz`

Expected output:

```text
X_images.shape  = (samples, 64, 64, 1)
X_strokes.shape = (samples, max_points, features)
y.shape         = (samples,)
```

---

### Phase 3: Letter Recognition Model

Goal: train a hybrid neural network for individual character recognition.

Tasks:

- [x] Build CNN branch for image input
- [x] Build GRU branch for stroke input
- [x] Concatenate image and stroke features
- [x] Train classifier on uppercase and lowercase English letters
- [x] Evaluate accuracy
- [x] Add prediction in app
- [x] Create prediction API
- [x] Create confusion matrix
- [x] Save classification report and training plots
- [x] Collect more data
- [x] Analyze incorrect predictions
- [x] Try data augmentation
- [ ] Compare three approaches:
  - image-only model
  - stroke-only model
  - hybrid model

---

### Phase 4: Extended Character Set

Goal: support more writing systems, digits, and symbols.

Planned classes:

```text
A-Z
a-z
0-9
.,!?+-*/=()[]{}@#$%
```

Future alphabets:

- Japanese kana
- Cyrillic
- other alphabets

---

### Phase 5: Word Recognition

Goal: move from single-character recognition to word-level recognition.

Planned architecture:

```text
Word image + stroke sequence
        ↓
CNN + sequence model
        ↓
CTC / sequence decoder
        ↓
recognized word
```

Examples:

```text
hello
machine
data
learning
```

This stage will require a different output structure because the model will need to predict a sequence of characters instead of a single class.

---

## How to Run

### 1. Create virtual environment

```powershell
python -m venv .venv
```

### 2. Install dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. Start backend

From the project root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.backend.main:app --reload --host 0.0.0.0 --port 8000
```

Backend:

```text
http://127.0.0.1:8000
```

### 4. Start frontend

Open a second terminal:

```powershell
cd app/frontend
..\..\.venv\Scripts\python.exe -m http.server 5500 --bind 0.0.0.0
```

Frontend:

```text
http://127.0.0.1:5500
```

To open the application from another device on the same Wi-Fi network, find the computer's IPv4 address:

```powershell
ipconfig
```

Then open:

```text
http://YOUR_IPV4:5500
```

### 5. Check and build the dataset

Run from the project root:

```powershell
.\.venv\Scripts\python.exe src/training/check_raw_dataset.py
.\.venv\Scripts\python.exe src/training/build_dataset.py
```

### 6. Train and evaluate the model

```powershell
.\.venv\Scripts\python.exe src/training/train.py
.\.venv\Scripts\python.exe src/evaluation/plot_confusion_matrix.py
```

### 7. Run prediction

1. Open the frontend in a browser.
2. Draw a letter on the canvas.
3. Click **Predict**.
4. Check the prediction and confidence values below the canvas.

> The backend and frontend must run at the same time in separate terminals. Press `Ctrl + C` to stop either server.

---

## API Endpoint

### Save sample

```http
POST /save-sample
```

Request body:

```json
{
  "label": "A",
  "image": "base64_png_image",
  "strokes": [
    {
      "x": 120,
      "y": 300,
      "t": 0,
      "pressure": 0.5,
      "pen_down": true
    }
  ],
  "canvas_width": 400,
  "canvas_height": 400
}
```

Response:

```json
{
  "status": "saved",
  "label": "A",
  "image_path": "data/raw/images/upper_A/upper_A_timestamp.png",
  "stroke_path": "data/raw/strokes/upper_A/upper_A_timestamp.json",
  "points_count": 128,
  "samples_count": 100
}
```

### Predict character

```http
POST /predict
```

Request body:

```json
{
  "image": "base64_png_image",
  "strokes": [
    {
      "x": 120,
      "y": 300,
      "t": 0,
      "pressure": 0.5,
      "pen_down": true
    }
  ],
  "canvas_width": 400,
  "canvas_height": 400
}
```

Response:

```json
{
  "prediction": "A",
  "confidence": 0.96,
  "top_3": [
    {
      "label": "A",
      "confidence": 0.96
    },
    {
      "label": "H",
      "confidence": 0.02
    },
    {
      "label": "R",
      "confidence": 0.01
    }
  ]
}
```

---

## Dataset Collection Target

Initial target:

```text
52 classes:
A-Z + a-z
```

Minimum dataset size:

```text
52 classes × 50 samples = 2,600 samples
```

Better target:

```text
52 classes × 100 samples = 5,200 samples
```

Current raw dataset:

```text
4,761 paired PNG + JSON samples
Dataset expansion to at least 100 samples per class is in progress
```

Current processed dataset:

```text
2,600 samples
52 classes x 50 samples
```

Future target:

```text
52 classes × 300 samples = 15,600 samples
```

---

## Results

The first hybrid model experiments were trained on the processed dataset with 2,600 samples.

| Model | Accuracy | Notes |
|---|---:|---|
| CNN image-only | TBD | Baseline model |
| Stroke-only LSTM / GRU | TBD | Sequence model |
| Hybrid CNN + GRU | 94.62% | Best current experiment, learning rate 0.0005 |

The current result uses a random train/validation/test split. Future evaluation should also use separate handwriting sessions and data from different writers.

---

## Learning Goals

This project is designed to practice and demonstrate:

- data collection for machine learning
- frontend and backend integration
- working with handwritten input
- image preprocessing
- sequence preprocessing
- CNN architecture
- LSTM / GRU sequence modeling
- hybrid neural network design
- model evaluation
- real-world ML pipeline design

---

## Project Status

Current status:

```text
Working MVP with data collection, preprocessing, training, evaluation, and prediction
```

Next major step:

```text
Complete the balanced dataset, rebuild it, retrain the hybrid model, and compare it with image-only and stroke-only models
```
