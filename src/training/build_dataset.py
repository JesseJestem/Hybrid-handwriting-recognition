from pathlib import Path
import sys
import json
import numpy as np

BASE_DIR = Path(__file__).resolve().parent[2] #Hybrid_handwriting_recognition/
sys.path.append(str(BASE_DIR)) #to import files from src/

#import preprocess function
from src.preprocessing.image_preprocessing import preprocess_image
from src.preprocessing.stroke_preprocessing import preprocess_strokes

IMAGE_DIR = BASE_DIR / "data" / "raw" / "images"
STROKE_DIR = BASE_DIR / "data" / "raw" / "strokes"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

DATASET_PATH = PROCESSED_DIR / "dataset.npz" #save numpy arrays: X_images, X_strokes, Y, class_names, display_labels
METADATA_PATH = PROCESSED_DIR / "dataset_metadata.json" #metadata: img size, stroke points, sample num, classes name, wrong samples

IMAGE_SIZE = 64
STROKE_SIZE = 100

#folder name to label: upper_A → A, lower_a → a
def folder_to_label(folder_name: str) -> str: 
    
    if folder_name.startswith("upper_"):
        return folder_name.replace("upper_", "", 1)
    if folder_name.startswith("lower_"):
        return folder_name.replace("lower_", "", 1)
    
    #if else: return just full names - for another symbhols
    return folder_name

#take list of classes name
def class_to_folders() -> list[str]:

    #take name of folders: upper_A, lower_a
    image_classes = sorted([p.name for p in IMAGE_DIR.iterdir() if p.is_dir()])
    stroke_classes = sorted([p.name for p in STROKE_DIR.iterdir() if p.is_dir()])

    image_class_set = set(image_classes)
    stroke_class_set = set(stroke_classes)

    missing_in_images = sorted(stroke_class_set - image_class_set)
    missing_in_strokes = sorted(image_class_set - stroke_class_set)
    
    if missing_in_images or missing_in_strokes:
        print("Class folders not matches")

        if missing_in_images:
            print ("Folders that exist in strokes but not in images:")
            for class_name in missing_in_images:
                print("-", class_name)
        
        if missing_in_strokes:
            print("Folders that exist in images but not in strokes:")
            for class_name in missing_in_strokes:
                print("-",class_name)
        
        #stop program running, dont training model in uncorrect data
        raise RuntimeError("Image/stroke class folders mismatch")
    
    return image_classes

#take image + stroke and merge it to one dict in list: {"class_folder": "upper_A", "label": "A","class_index": 0,"image_path": "...png", "stroke_path": "...json"}
def collect_sample_pairs(class_folders: list[str]) -> list[dict]:

    samples = []

    #take index of folder and name
    for class_index, class_folder in enumerate(class_folders):
        image_class_dir = IMAGE_DIR / class_folder
        stroke_class_dir = STROKE_DIR / class_folder

        #take all images
        image_files = sorted(image_class_dir.glob("*.png"))

        #search jsom for every image
        for image_path in image_files:
            stroke_path = stroke_class_dir / f"{image_path.stem}.json" #take only file name: upper_A_20260525_120000_123456

            #skip file if image doesnt exists
            if not stroke_path.exists():
                print(f"Missing stroke file for image: {image_path}")
                continue

            samples.append(
                {
                    "class_folder": class_folder,
                    "label": folder_to_label(class_folder),
                    "class_index": class_index,
                    "image_path": image_path,
                    "stroke_path": stroke_path,
                }
            )

    return samples