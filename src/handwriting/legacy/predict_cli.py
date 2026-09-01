import argparse  # allow run a file from the terminal with arguments (send path to img and stroke)
from pathlib import Path

#import predictions def
from handwriting.legacy.predictor import predict_from_files

BASE_DIR = Path(__file__).resolve().parents[2]

#~~~~~~~~~~~~~~~~~~~~
#main file runing (in CMD without rest API)
#~~~~~~~~~~~~~~~~~~~

def main():
    parser  = argparse.ArgumentParser()

    parser.add_argument("--image", required=True, help="Path to PNG image")
    parser.add_argument("--strokes", required=True, help="Path to JSON strokes")
    parser.add_argument("--top_k", type=int, default=3)

    args = parser.parse_args()

    result = predict_from_files(
        image_path=args.image,
        stroke_path=args.strokes,
        top_k=args.top_k,
    )

    print("Prediction:", result["prediction"])
    # 100 -> 0,94 to 94%, 2 - zeros after 0,00
    print("Confidence:", round(result["confidence"] * 100, 2), "%")
    print()
    print("Top predictions:")

    for item in result["top_k"]:
        print(f"{item['label']}: {item['confidence']:.4f}")


if __name__ == "__main__":
    main()