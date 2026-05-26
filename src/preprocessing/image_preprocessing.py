from pathlib import Path
#using PIL to process images (editor)
from PIL import Image
import numpy as np

#str | Path image path, -> np.ndarray - says that we recive array at output
def preprocess_image(image_path: str | Path, image_size: int = 64) -> np.ndarray:

    image_path = Path(image_path)

    image = Image.open(image_path).convert("L") # open image as gray scale 255-white, 0-black. P.S. color - R, G, B
    image_array = np.array(image) #convert image in array

    mask = image_array < 250 #find not white px as true/false

    if not np.any(mask): #find true in mask
        return np.zeros((image_size, image_size, 1), dtype = np.float32) #if no - return zeros array

    y_indices, x_indices = np.where(mask) #take all true px coordinate y-vertical, x-horizontal, image_array[y][x]

    #take borders of letter
    x_min,x_max = x_indices.min(), x_indices.max()
    y_min,y_max = y_indices.min(), y_indices.max()

    #crop only letter
    cropped = image.crop((x_min, y_min, x_max + 1, y_max + 1)) #left, top, right, bottom (+1 brcause last px will be cropped)

    #add padding to centrate image
    padding = 20
    padded_width = cropped.width + padding * 2 #left + right
    padded_heigth = cropped.height + padding * 2 #top + bottom

    #create new white img + paste cropped letter with paddings
    padded = Image.new("L", (padded_width, padded_heigth), color = 255)
    padded.paste(cropped,(padding,padding)) #image, coordinate x,y

    #resize = thumbnail-save proportion[y,x], Image.Resampling.LANCZOS-change image size algoritm-saving data quality
    padded.thumbnail((image_size, image_size), Image.Resampling.LANCZOS)

    #create final white img
    final_image = Image.new("L", (image_size, image_size), color = 255)

    #paste in center of new final img
    paste_x = (image_size - padded.width) // 2
    paste_y = (image_size - padded.height) // 2

    final_image.paste(padded, (paste_x, paste_y))

    #convert new img in np.array
    final_array = np.array(final_image).astype(np.float32)

    #normalize and invert 0-255 to 0-1 and reverse 0-black, 1-white
    final_array = 1.0 - (final_array / 255.0)

    #add chanel (64,64) -> (64,64,1)
    final_array = np.expand_dims(final_array, axis = -1)

    return final_array.astype(np.float32)

#test code
if __name__ == "__main__":
    test_path = Path("data/raw/images/upper_A")
    if test_path.exists():
        first_image = next(test_path.glob("*.png"))
        processed = preprocess_image(first_image)
        print("Processed image shape:", processed.shape)
        print("Min:", processed.min())
        print("Max:", processed.max())