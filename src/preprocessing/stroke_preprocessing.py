from pathlib import Path
import json
import numpy as np

#open stroke file as python dict
def load_stroke_json(stroke_path: str | Path) -> dict:
    stroke_path = Path(stroke_path)

    with open(stroke_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data

#retutn normalized strokes in range 0-1 in formate [num_points, 5]
def normalize_strokes (data: dict) -> np.array:

    strokes = data.get("strokes", []) #if not - empty list
    
    if len(strokes) == 0:
        return np.zeros((0, 5), dtype=np.float32) #emtpy list - zeros
    
    #take stroke data and convert it into np.array
    x_values = np.array([p["x"] for p in strokes], dtype=np.float32)
    y_values = np.array([p["y"] for p in strokes], dtype=np.float32)
    t_values = np.array([p["t"] for p in strokes], dtype=np.float32)

    pressure_values = np.array([p.get("pressure", 0.5) for p in strokes], dtype=np.float32)
    pen_down_values = np.array([1.0 if p.get("pen_down", True) else 0.0 for p in strokes], dtype=np.float32)

    #normalize data

    #normalize coordinate
    #take borders of letter
    x_min, x_max = x_values.min(), x_values.max()
    y_min, y_max = y_values.min(), y_values.max()
    t_min, t_max = t_values.min(), t_values.max()

    #take width, height, scale - proportion
    width = x_max - x_min
    height = y_max - y_min
    scale = max(width, height)

    #if scale too low - set zeros to not divide by 0
    if scale < 1e-6:
        x_norm = np.zeros_like(x_values)
        y_norm = np.zeros_like(y_values)

    #transform coordinate to 0-1 range
    else:
        x_norm = (x_values - x_min) / scale
        y_norm = (y_values - y_min) / scale 

        #set letter on center
        if width < scale:
            x_norm += (1.0 - width / scale) / 2.0

        if height < scale:
            y_norm += (1.0 - height / scale) / 2.0

    x_norm = np.clip(x_norm, 0.0, 1.0)
    y_norm = np.clip(y_norm, 0.0, 1.0)

    #normalize time
    t_min, t_max = t_values.min(), t_values.max()

    #transform time to 0-1 range
    if t_max - t_min < 1e-6:
        t_norm = np.zeros_like(t_values)
    
    else:
        t_norm = (t_values - t_min) / (t_max - t_min)

    #cut pressure to range 0-1
    pressure_values = np.clip(pressure_values, 0.0, 1.0)

    #collect all normalize features to np.array and return
    features = np.stack(
        [
            x_norm,
            y_norm,
            t_norm,
            pressure_values,
            pen_down_values,
        ],
        axis=1
    )

    return features.astype(np.float32)

#set stroke points fixed to 100 and return np.ndarray
def resample_strokes(strokes: np.ndarray, max_points: int = 100) ->np.ndarray:

    #if no points return zeros (100, 5)
    if len(strokes) == 0:
        return np.zeros((max_points, 5), dtype=np.float32)
    
    #if only 1 point return this point * 100 (100, 5)
    if len(strokes) == 1:
        repeated = np.repeat(strokes, max_points, axis=0)
        return repeated.astype(np.float32)
    

    #interpolation - search unknown points from known to fill all 100 points

    #create old and new point position index (5, 1) -> (100, 1) in range 0-1, np.linspace - create smooth scale from 0 to 1
    old_indices = np.linspace(0, 1, num=len(strokes))
    new_indices = np.linspace(0, 1, num=max_points)

    resampled_features = []

    #in range of features count (16, 5) (x,y,t,p,pen) take 5 features and interpolate old(16) to new(100) and create
    #new list of features with 100 values
    for feature_index in range(strokes.shape[1]):
        feature_values = strokes[:, feature_index] #take all collum of every feature
        resampled = np.interp(new_indices, old_indices, feature_values) # fill empty spase old16-new100 by features
        resampled_features.append(resampled)

        #Example:
        #old_indices = [0.0, 1.0]
        #feature_values = [10, 20]
        #new_indices = [0.0, 0.5, 1.0]
        #np.interp = [10, 15, 20] because 15 in the middle 10-20

    #collect all features back to formate (x,y,t,p,pen)
    resampled_strokes = np.stack(resampled_features, axis=1)

    #return pen_down only to 1.0 or 0.0 formate (cancell interpolation) if 0.5 and more = 1.0 else 0.0
    resampled_strokes[:, 4] = (resampled_strokes[:, 4] >= 0.5).astype(np.float32)

    #return new full (100, 5) formate stroke
    return resampled_strokes.astype(np.float32)

#main pipeline: json -> load data -> norm -> inetpolation -> complete
def preprocess_strokes(stroke_path: str | Path, max_points: int = 100) ->np.ndarray:

    data = load_stroke_json(stroke_path)
    normalized = normalize_strokes(data)
    resampled = resample_strokes(normalized, max_points=max_points)

    return resampled

#test code
if __name__ == "__main__":
    test_path = Path("data/raw/strokes/upper_A")
    if test_path.exists():
        first_json = next(test_path.glob("*.json"))
        processed = preprocess_strokes(first_json)
        print("Processed strokes shape:", processed.shape)
        print("Min:", processed.min())
        print("Max:", processed.max())