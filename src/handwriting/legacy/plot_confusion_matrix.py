from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

#~~~~~~~~~~~~~~~~~~~~~
#Set path and dirs
#~~~~~~~~~~~~~~~~~~~~~

BASE_DIR = Path(__file__).resolve().parents[2]

DATASET_PATH = BASE_DIR / "data" / "processed" / "dataset.npz"
CONFUSION_MATRIX_PATH =  BASE_DIR / "outputs" / "confusion_matrix.npy"
OUTPUT_DIR = BASE_DIR / "outputs"

#~~~~~~~~~~~~~~~~~~~
#Conf matrix
#~~~~~~~~~~~~~~~~~~~

def  plot_confusion_matrix():
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATASET_PATH}")
    
    if not CONFUSION_MATRIX_PATH.exists():
        raise FileNotFoundError(f"Confusion matrix not found: {CONFUSION_MATRIX_PATH}")
    
    #~~~~~~~~~~~~~~~~~~~~~
    #Load all datasets
    #~~~~~~~~~~~~~~~~~~~~~
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    data = np.load(DATASET_PATH, allow_pickle=True)
    display_labels = data["display_labels"]

    cm = np.load(CONFUSION_MATRIX_PATH)

    #~~~~~~~~~~~~~~~~~~~~~~~~~
    #Row normalization
    #~~~~~~~~~~~~~~~~~~~~~~~~~

    #take sum of all rows and save it as 2D array
    row_sums = cm.sum(axis=1, keepdims=True)
    #divide predictions to all samples and shows % of mistake
    cm_normalized = np.divide(
        cm,
        row_sums,
        out=np.zeros_like(cm, dtype=np.float32), #if no data set result as zeros
        where=row_sums !=0, #does not divide to 0
    )

    #plot drawing
    plt.figure(figsize=(18, 18)) #size of img
    plt.imshow(cm_normalized, interpolation='nearest') #print img without smoothing
    plt.title('Normalized Confusion Matrix')
    plt.xlabel('Predicted label')
    plt.ylabel('True label')
    plt.colorbar() #add color bar to plot
    
    #set x and y labels in plot
    tick_marks = np.arange(len(display_labels))
    plt.xticks(tick_marks, display_labels)
    plt.yticks(tick_marks, display_labels)

    #save img
    plt.tight_layout() #add paddings
    plt.savefig(OUTPUT_DIR / 'confusion_matrix.png', dpi=200) #dpi = img qa
    plt.close()

    print('Saved confusion matrix to:', OUTPUT_DIR / 'confusion_matrix.png')

    #~~~~~~~~~~~~~~~~~~~~~
    #Print bigges mistakes
    #~~~~~~~~~~~~~~~~~~~~~

    mistakes = []

    #search for miatskes + add it to miss list
    for true_index in range(cm.shape[0]):
        for pred_index in range(cm.shape[1]):
            if true_index == pred_index:
                continue

            count = cm[true_index, pred_index]

            if count > 0:
                mistakes.append(
                    (
                    count,
                    display_labels[true_index],
                    display_labels[pred_index],
                    )
                )
    
    #show top miss for the first
    mistakes = sorted(mistakes, reverse=True)

    print()
    print("Top mistakes")
    for count, true_label, pred_label in mistakes[:20]:
        print(f'true: {true_label} -> predicted: {pred_label}, count: {count}')

if __name__ == '__main__':
    plot_confusion_matrix()