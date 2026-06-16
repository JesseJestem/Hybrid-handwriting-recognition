import argparse # allow run a file from the terminal with arguments (send path to img and stroke)

#import predictions def
from src.inference.predictor import predict_from_files

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
    print("Confidence:", round(result["confidence"] * 100, 2), "%") #100 -> 0,94 to 94%, 2 - zeros after 0,00
    print()
    print("Top predictions:")

    for item in result["top_k"]:
        print(f"{item['label']}: {item['confidence']:.4f}")


if __name__ == "__main__":
    main()