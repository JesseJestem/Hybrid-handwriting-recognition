from pathlib import Path
import json

BASE_DIR = Path(__file__). resolve().parents[2]
IMAGE_DIR = BASE_DIR / "data" / "raw" / "images"
STROKE_DIR = BASE_DIR / "data" / "raw" / "strokes"

def check_dataset ():
    total_images = 0
    total_strokes = 0
    problems = []

    #iterdir - take all objects from images, take only folders - is_dir, take only names - p.name,
    #create list of pathes - ["A","a","B"...]
    image_classes = sorted([p.name for p in IMAGE_DIR.iterdir() if p.is_dir()])
    stroke_classes = sorted([p.name for p in STROKE_DIR.iterdir() if p.is_dir()])

    #print total classes in raw data
    print("Image classes :", len(image_classes))
    print("Stroke classes :", len(stroke_classes))
    print()

    #check and print name of missing classes in every part
    image_class_set = set(image_classes)
    stroke_class_set = set(stroke_classes)

    missing_strokes = sorted(image_class_set - stroke_class_set)
    missing_images = sorted(stroke_class_set - image_class_set)

    if missing_images or missing_strokes:
        print("Classes don't match!")

        if missing_images:
            print("Missing images:")

            for class_name in missing_images:
                print(f"- {class_name}")

        if missing_strokes:
            print("Missing strokes:")

            for class_name in missing_strokes:
                print(f"- {class_name}")

        return
    
    #print file count for every classes of img and strk
    for class_name in image_classes:
        image_files = sorted((IMAGE_DIR / class_name).glob("*.png")) #search all png files
        stroke_files = sorted((STROKE_DIR / class_name).glob("*.json")) #search all png filesss

        total_images += len(image_files)
        total_strokes += len(stroke_files)

        print(f"{class_name}: images:={len(image_files)},  strokes:{len(stroke_files)}")

        #append if some file missing
        if len(image_files) != len(stroke_files):
            problems.append(f"{class_name}: image/stroke count missmatch")

        #checking file content and append
        for stroke_file in stroke_files:
            with open(stroke_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            strokes = data.get("strokes", [])

            if len(strokes) < 5:
                problems.append(f"{stroke_file}: too few stroke points")

            if "label" not in data:
                problems.append(f"{stroke_file}: missing label")

            if "canvas_width" not in data or "canvas_height" not in data:
                problems.append(f"{stroke_file}: missing canvas size")

    #print file totals in classes
    print()
    print("Total images:", total_images)
    print("Total strokes:", total_strokes)

    print()
    if problems:
        print("Problems found:")
        for problem in problems:
            print(f"- {problem}")
    
    else:
        print("Problem not found")
        

if __name__ == "__main__":
    check_dataset()