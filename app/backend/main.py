from fastapi import FastAPI
#for different servers
from fastapi.middleware.cors import CORSMiddleware 
# create model of request
from pydantic import BaseModel 
# convinient file pass
from pathlib import Path
# create unique name based on time
from datetime import datetime
import base64
import json

app = FastAPI()

#allow to send request to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"], #allow all websites
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

BASE_DIR = Path(__file__).resolve().parents[2] #take absolute file path from 2 lvl above (project folder)
IMAGE_DIR = BASE_DIR / "data" / "raw" / "images" #save images in data/raw/images/A/1image.png
STROKE_DIR = BASE_DIR / "data" / "raw" / "strokes" #save strokes in data/raw/strokes/A/1stroke.png
#create folder if not exist
IMAGE_DIR.mkdir(parents=True, exist_ok=True)
STROKE_DIR.mkdir(parents=True, exist_ok=True)

class Point(BaseModel):
    x: float
    y: float
    t: float
    pressure: float
    pen_down: bool

#api reqest model
class SampleRequest(BaseModel):
    label: str #letter,number,symbhol
    image: str #base64 image
    strokes: list[Point] #list with moving [x, y, time]
    canvas_width: int
    canvas_height: int

#create test endpoint: if open http://localhost:8000/ "/" - def root will start and ansver with message
@app.get("/")
def root():
    return{"message": "Hybrid Handwriting Data Collection API"}

#create sample save endpoint
@app.post("/save-sample")
#take JSON from request and check model SampleRequest after transform to python-object sample.
def save_sample(sample: SampleRequest):
    label = sample.label #create folder for every letter or symbhol

    #create folders for every symhol
    image_label_dir = IMAGE_DIR / label #data/raw/images/A
    stroke_label_dir = STROKE_DIR / label #data/raw/strokes/A

    image_label_dir.mkdir(parents=True, exist_ok=True)
    stroke_label_dir.mkdir(parents=True, exist_ok=True)
    
    #create uniqe timestamp mark
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    #create name of files
    image_filename = f"{label}_{timestamp}.png"
    stroke_filename = f"{label}_{timestamp}.json"

    #create file path
    image_path = image_label_dir / image_filename
    stroke_path = stroke_label_dir / stroke_filename

    #from data:image/png;base64,dhHBhvh2hvH... take second base part and decode it
    image_data = sample.image.split(",")[1] 
    image_bytes = base64.b64decode(image_data)

    with open (image_path, "wb") as f: #wb - png is binary file so save as write binary
        f.write(image_bytes)

    #prepare stroke data creating dict with data
    stroke_data = {
        "label": label,
        "image_path": str(image_path),
        "canvas_width": sample.canvas_width,
        "canvas_height": sample.canvas_height,
        "strokes": [point.model_dump() for point in sample.strokes], #save as dict
    }

    with open(stroke_path, "w", encoding="utf-8") as f:
        #save dict as JSON, ensure_ascii=False - no englis aslo ok, indent=2 - create readeble structure
        json.dump(stroke_data, f, ensure_ascii=False, indent=2)

    #count total of examples
    samples_count = len(list(image_label_dir.glob("*.png")))

    return{
        "status": "saved",
        "label": label,
        "image_path": str(image_path),
        "stroke_path": str(stroke_path),
        "points_count": len(sample.strokes),
        "samples_count": samples_count,
    }