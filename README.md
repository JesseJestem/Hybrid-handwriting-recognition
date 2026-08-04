# Hybrid Handwriting Recognition

## Project Overview

This project is a handwriting recognition system for handwritten input from a mouse, touchpad, touchscreen, or stylus.

The current goal is to build a data collection application for handwritten English letters. The collected data will later be used to train a hybrid neural network that combines image-based recognition and stroke-based recognition.

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

The project is currently in creating first hybrid moded stage.

The application allows the user to:

- select a character label
- draw a handwritten character on a canvas
- save the drawing as a PNG image
- save stroke coordinates as JSON data
- collect a custom dataset for future model training

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

## Planned Model Architecture

The planned first model will classify individual English letters.

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

### Future Machine Learning Stack

- TensorFlow / Keras
- NumPy
- OpenCV
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
- [x] Test run

### In Progress

- [ ] Confusin matrix
- [ ] Prediction tool
- [ ] Collect more data
- [ ] CNN image model
- [ ] Stroke-based sequence model

### Planned

- [ ] Model evaluation
- [ ] Data augmentation
- [ ] Data synthesis
- [ ] Confusion matrix
- [ ] Prediction API
- [ ] Real-time character prediction
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
- [ ] Add prediction in app
- [ ] Collect more data
- [ ] Confision matrix
- [ ] Analyze incorrect predictions
- [ ] Try data augmentation
- [ ] Try data synthesis
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

If TensorFlow is missing or broken:

```powershell
.\.venv\Scripts\python.exe -m pip install tensorflow
```

---

## Run Locally

Use this if you open the app on the same computer.

### Start backend

From the project root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.backend.main:app --reload --host 127.0.0.1 --port 8000
```

### Start frontend

Open a second terminal:

```powershell
cd app/frontend
..\..\.venv\Scripts\python.exe -m http.server 5500 --bind 127.0.0.1
```

Open in browser:

```text
http://127.0.0.1:5500
```

---

## Run on Local Wi-Fi Network

Use this if you want to open the app from another device on the same Wi-Fi network.

### 1. Find your computer IPv4

```powershell
ipconfig
```

Example:

```text
192.168.1.35
```

### 2. Start backend

From the project root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Start frontend

Open a second terminal:

```powershell
cd app/frontend
..\..\.venv\Scripts\python.exe -m http.server 5500 --bind 0.0.0.0
```

Open in browser:

```text
http://YOUR_IPV4:5500
```

Example:

```text
http://192.168.1.35:5500
```

---

## Notes

* Backend and frontend must run at the same time.
* Use two separate terminal windows.
* `0.0.0.0` is only for server binding. Do not open it in the browser.
* To stop a server, press `Ctrl + C`.
* If Windows Firewall asks for permission, allow Python on private networks.

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
  "points_count": 128,
  "samples_count": "2",

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

Future target:

```text
52 classes × 300 samples = 15,600 samples
```

---

## Future Results Section

After training the first models, the results will be added here.

| Model | Accuracy | Notes |
|---|---:|---|
| CNN image-only | TBD | Baseline model |
| Stroke-only LSTM / GRU | TBD | Sequence model |
| Hybrid CNN + LSTM / GRU | TBD | Main model |

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
Training first hybrid model in progress
```

Next major step:

```text
Create CNN image model and stroke-based sequence model
```
