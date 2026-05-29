from pathlib import Path
import sys
import json
import numpy as np

BASE_DIR = Path(__file__).resolve().parents[2] #Hybrid_handwriting_recognition/
sys.path.append(str(BASE_DIR)) #to import files from src/

#import preprocess function
from src.preprocessing.image_preprocessing import preprocess_image
from src.preprocessing.stroke_preprocessing import preprocess_strokes

IMAGE_DIR = BASE_DIR / "data" / "raw" / "images"
STROKE_DIR = BASE_DIR / "data" / "raw" / "strokes"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

DATASET_PATH = PROCESSED_DIR / "dataset.npz" #save numpy arrays: X_images, X_strokes, y, class_names, display_labels
METADATA_PATH = PROCESSED_DIR / "dataset_metadata.json" #metadata: img size, stroke points, sample num, classes name, wrong samples

IMAGE_SIZE = 64
MAX_POINTS = 100

#folder name to label: upper_A → A, lower_a → a
def folder_to_label(folder_name: str) -> str: 
    
    if folder_name.startswith("upper_"):
        return folder_name.replace("upper_", "", 1)
    if folder_name.startswith("lower_"):
        return folder_name.replace("lower_", "", 1)
    
    #if else: return just full names - for another symbhols
    return folder_name

#take list of classes name
def get_class_folders() -> list[str]:

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

            #skip file if stroke doesnt exists
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

def build_dataset():

    #display info about start building
    print("Building dataset...")
    print("Base dir:", BASE_DIR)
    print("Image dir:", IMAGE_DIR)
    print("Stroke dir:", STROKE_DIR)

    #create processed folder if doesnt exist
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    class_folders = get_class_folders()

    #display info about classes
    print("Classes found: ", len(class_folders))
    for index, class_name in enumerate(class_folders):
        print(f"{index}:{class_name} -> {folder_to_label(class_name)}")

    print()

    #collect all samples
    samples = collect_sample_pairs(class_folders)

    if len(samples) == 0:
        raise RuntimeError("No samples found")
    
    print("Total mached samples: ", len(samples))
    print()

    #create data lists for dataset
    X_images = []
    X_strokes = []
    y = []
    failed_samples = []

    for index, sample in enumerate(samples, start=1):
        image_path = sample["image_path"]
        stroke_path = sample["stroke_path"]
        class_index = sample["class_index"]

        try:
            image_array = preprocess_image(
                image_path=image_path,
                image_size=IMAGE_SIZE
            )

            stroke_array = preprocess_strokes(
                stroke_path=stroke_path,
                max_points=MAX_POINTS
            )

            #adding data to dataset
            X_images.append(image_array) #image
            X_strokes.append(stroke_array) #stroke
            y.append(class_index) #correct letter

        #find and print errors
        except Exception as e:
            failed_samples.append(
                {
                    "image_path": str(image_path),
                    "stroke_path": str(stroke_path),
                    "error": str(e),
                }
            )

        #progress display
        if index % 100 == 0:
            print(f"Processed {index}/{len(samples)} samples")

    #convert py.array into np.array
    X_images = np.array(X_images, dtype=np.float32)
    X_strokes = np.array(X_strokes, dtype=np.float32)
    y = np.array(y, dtype=np.int64) #ints - number of classes: 1, 2, 3...
    class_names = np.array(class_folders) #upper_A
    display_labels = np.array([folder_to_label(name) for name in class_folders]) #A

    #display sample shape info
    print()
    print("Dataset shapes:")
    print("X_images: ", X_images.shape)
    print("X_strokes: ", X_strokes.shape)
    print("y: ", y.shape)
    print("class_names: ", class_names.shape)
    print("display_labels: ", display_labels.shape)

    print()
    print("Fale samples: ", len(failed_samples))

    #save data in .npz compressed-file
    np.savez_compressed(
        DATASET_PATH,
        X_images=X_images,
        X_strokes=X_strokes,
        y=y,
        class_names=class_names,
        display_labels=display_labels,
    )

    #save metadata dict for documentation
    metadata = {
        "dataset_path": str(DATASET_PATH),
        "image_size": IMAGE_SIZE,
        "max_points": MAX_POINTS,
        "stroke_features": [
            "x_norm",
            "y_norm",
            "t_norm",
            "pressure",
            "pen_down",
        ],
        "num_samples": int(len(y)),
        "num_classes": int(len(class_names)),
        "class_names": class_names.tolist(),
        "display_labels": display_labels.tolist(),
        "failed_samples": failed_samples,
    }

    with open (METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print()
    print("Saved dataset to: ", DATASET_PATH)
    print("Saved metadata to: ", METADATA_PATH)

if __name__ == "__main__":
    build_dataset()