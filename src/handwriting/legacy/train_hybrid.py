import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

from handwriting.models.hybrid import build_hybrid_model
from handwriting.training.augmentation import augment_training_data

#GPU SETTINGS
GPU_DEVICES = tf.config.list_physical_devices("GPU")

print("TensorFlow:", tf.__version__)
print("GPU devices:", GPU_DEVICES)

for gpu in GPU_DEVICES:
    tf.config.experimental.set_memory_growth(gpu, True)

#add path for import
BASE_DIR = Path(__file__).resolve().parents[3]

DATASET_PATH = BASE_DIR / "data" / "processed" / "dataset.npz"
OUTPUT_DIR = BASE_DIR / "outputs" #result folder
MODEL_DIR = BASE_DIR / "saved_models"

#result path
MODEL_PATH = MODEL_DIR / "hybrid_letters.keras"
REPORT_PATH = OUTPUT_DIR / "classification_report.txt"
CONFUSION_MATRIX_PATH = OUTPUT_DIR / "confusion_matrix.npy"
HISTORY_PATH = OUTPUT_DIR / "training_history.png"

#~~~~~~~~~~~~~~~~~~~~~~~
#MODEL SETTINGS
#~~~~~~~~~~~~~~~~~~~~~~~

RANDOM_STATE = 42 #makes train/val/test split reproducible
BATCH_SIZE = 32
EPOCHS = 70
TRAIN_RATE = 0.0005
AUGMENT_COPIES = 5

#~~~~~~~~~~~~~~
#check if dataset file exist?
#~~~~~~~~~~~~~~

def load_dataset():
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Dataset not found:{DATASET_PATH}\n"
                                "Run build_dataset.py first")

    #load dataset from .npz
    # allow to load python objects from file (X_images, X_strokes...)
    data = np.load(DATASET_PATH, allow_pickle=True)

    X_images = data["X_images"]
    X_strokes = data["X_strokes"]
    y = data["y"]
    class_names = data["class_names"]
    display_labels = data["display_labels"]

    print("Dataset loaded:")
    print("X_images:", X_images.shape)
    print("X_strokes:", X_strokes.shape)
    print("y:", y.shape)
    print("class_names:", class_names.shape)
    print("display_labels:", display_labels.shape)
    print()

    return X_images, X_strokes, y, class_names, display_labels

#~~~~~~~~~~~~~~
#save training/validation accuracy and loss plot
#~~~~~~~~~~~~~~

def plot_training_history(history):

    acc = history.history["accuracy"]
    val_acc = history.history["val_accuracy"]
    loss = history.history["loss"]
    val_loss = history.history["val_loss"]
    epochs_range = range(1, len(acc) + 1)

    #accuracy plot
    plt.figure()
    plt.plot(epochs_range, acc, label="Training Accuracy")
    plt.plot(epochs_range, val_acc, label="Validation Accuracy")
    plt.xlabel("Epochs")
    plt.ylabel("Accuracy")
    plt.legend()
    plt.title("Training and Validation Accuracy")
    plt.savefig(OUTPUT_DIR / "accuracy.png")
    plt.close()

    #loss plot
    plt.figure()
    plt.plot(epochs_range, loss, label="Training Loss")
    plt.plot(epochs_range, val_loss, label="Validation Loss")
    plt.xlabel("Epochs")
    plt.ylabel("Loss")
    plt.legend()
    plt.title("Training and Validation Loss")
    plt.savefig(OUTPUT_DIR / "loss.png")
    plt.close()

#~~~~~~~~~~~~~~~~~~~~~~~
#Model Training
#~~~~~~~~~~~~~~~~~~~~~~~

def train():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    #take data from dataset
    X_images, X_strokes, y, class_names, display_labels = load_dataset()

    #output neuron num
    num_classes = len(class_names)

    #~~~~~~~~~~~~~~~~~
    #Tarin/temp - 70/30 - split
    # ~~~~~~~~~~~~~~~~~

    X_img_train, X_img_temp, X_str_train, X_str_temp, y_train, y_temp = train_test_split(
        X_images,
        X_strokes,
        y,
        test_size=0.3,
        random_state=RANDOM_STATE,
        stratify=y, #save proportion in split by y
    )

    # ~~~~~~~~~~~~~~~~~
    # CV/test - 30 = 15/15 - split
    # ~~~~~~~~~~~~~~~~~

    X_img_val, X_img_test,X_str_val, X_str_test,y_val, y_test = train_test_split(
        X_img_temp,
        X_str_temp,
        y_temp,
        test_size=0.5,
        random_state=RANDOM_STATE,
        stratify=y_temp,
    )

    print("Split shapes:")
    print("Train images:", X_img_train.shape)
    print("Val images:", X_img_val.shape)
    print("Test images:", X_img_test.shape)
    print("Train strokes:", X_str_train.shape)
    print("Val strokes:", X_str_val.shape)
    print("Test strokes:", X_str_test.shape)
    print()

    # ~~~~~~~~~~~~~~~~~
    # Data augmentation only for train data
    # ~~~~~~~~~~~~~~~~~

    print("Before augmentation:")
    print("Train images:", X_img_train.shape)
    print("Train strokes:", X_str_train.shape)
    print("Train labels:", y_train.shape)
    print()

    X_img_train, X_str_train, y_train = augment_training_data(
        X_train_images=X_img_train,
        X_train_strokes=X_str_train,
        y_train=y_train,
        copies_per_sample=AUGMENT_COPIES,
    )

    print("After augmentation:")
    print("Train images:", X_img_train.shape)
    print("Train strokes:", X_str_train.shape)
    print("Train labels:", y_train.shape)
    print()

    #~~~~~~~~~~~~~~~~~~~~~
    #Model building
    #~~~~~~~~~~~~~~~~~~~~~
    
    model = build_hybrid_model(
        num_classes=num_classes,
        image_shape=X_images.shape[1:],
        stroke_shape=X_strokes.shape[1:],
    )

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=TRAIN_RATE),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=["accuracy"],
    )

    model.summary()

    # ~~~~~~~~~~~~~~
    #ModelCheckpoint + EarlyStopping + ReduceLROnPlateau
    # ~~~~~~~~~~~~~~

    callbacks = [
        #save best model
        tf.keras.callbacks.ModelCheckpoint(
            filepath=MODEL_PATH,
            monitor="val_accuracy", #checking by CV accuracy
            save_best_only=True,
            verbose=1, #display progress(long ver), 0 - dont display, 2- only epoch (short ver)
        ),
        #stop learning when no improving
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss", #checking by CV loss
            patience=5, #if no improve in 5 epoch - stop
            restore_best_weights=True, #save best w,b
            verbose=1,
        ),
        #reduce learning rate if model not improving
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5, #if no improving = learning rate/2
            patience=3,
            verbose=1,
        )
    ]

    # ~~~~~~~~~~~~~~
    #Save training statistic
    # ~~~~~~~~~~~~~~

    history = model.fit({
            #input same as in model
            "image_input": X_img_train,
            "stroke_input": X_str_train,
        },
        y_train,
        #CV block
        validation_data=(
            {
                "image_input": X_img_val,
                "stroke_input": X_str_val,
            },
            y_val,
        ),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        callbacks=callbacks,
    )

    print()
    print("Evaluating model on test data...")

    # ~~~~~~~~~~~~~~
    #Model checking by test set
    # ~~~~~~~~~~~~~~

    test_loss, test_accuracy = model.evaluate(
    {
            "image_input": X_img_test,
            "stroke_input": X_str_test,
        },
        y_test,
        verbose=0,
    )

    #result display
    print("Test loss:", test_loss)
    print("Test accuracy:", test_accuracy)

    # ~~~~~~~~~~~~~~
    #Predictions
    # ~~~~~~~~~~~~~~

    y_pred_logits = model.predict(
        {
            'image_input': X_img_test,
            'stroke_input': X_str_test,
        }
    )

    #take max value for each classes
    y_pred = np.argmax(y_pred_logits, axis=1)

    #~~~~~~~~~~~~~~
    #Report creating
    # ~~~~~~~~~~~~~~

    report = classification_report(
        y_test,
        y_pred,
        target_names=display_labels,
        zero_division=0, #if not found set 0
    )

    #confusion matrix
    cm = confusion_matrix(y_test, y_pred)

    with open(REPORT_PATH, "w", encoding='utf-8') as f:
        f.write(report)

    np.save(CONFUSION_MATRIX_PATH, cm)

    #save plots
    plot_training_history(history)

    #~~~~~~~~~~~~
    #Save final metadata
    #~~~~~~~~~~~~

    #report dic
    training_metadata = {
        'model_path': str(MODEL_PATH),
        'dataset_path': str(DATASET_PATH),
        'num_classes': int(num_classes),
        'class_names': class_names.tolist(),
        'display_labels': display_labels.tolist(),
        'test_loss': float(test_loss),
        'test_accuracy': float(test_accuracy),
        'batch_size': BATCH_SIZE,
        'epochs': EPOCHS,
        'learning_rate': TRAIN_RATE,
        'aug_copy_num': AUGMENT_COPIES,
    }

    with open(OUTPUT_DIR / "training_metadata.json", "w", encoding='utf-8') as f:
        json.dump(training_metadata, f, ensure_ascii=False, indent=2)

    #display results
    print()
    print("Saved model to:", MODEL_PATH)
    print("Saved report to:", REPORT_PATH)
    print("Saved confusion matrix to:", CONFUSION_MATRIX_PATH)
    print("Saved plots to:", OUTPUT_DIR)

if __name__ == "__main__":
    train()