import tensorflow as tf
from tensorflow.keras import layers, Model

def build_hybrid_model(
        num_classes: int, 
        image_shape: tuple[int, int, int] = (64, 64, 1), 
        stroke_shape: tuple[int, int] = (100, 5)
        ) -> Model:
    
    #~~~~~~~~~~~~~~~~~~
    # Image branch: CNN = Convolutional Neural Network (images)
    #~~~~~~~~~~~~~~~~~~

    #create input for images
    image_input = layers.Input(shape = image_shape, name = "image_input")

    #Conv2D - searching simple shapes (32) -> 64 x 64 x 32 image, serching in 3x3 px, same size as befre 64x64
    x = layers.Conv2D(
        filters=32,
        kernel_size=(3, 3),
        activation="relu",
        padding="same",
    )(image_input)
    #take biggest value from 2x2px and change shape -> 32 x 32 x 32
    x = layers.MaxPooling2D(pool_size=(2, 2))(x)

    #same layers but take more complicated shapes 32 -> 64
    x = layers.Conv2D(
        filters=64,
        kernel_size=(3, 3),
        activation="relu",
        padding="same",
    )(x)
    x = layers.MaxPooling2D(pool_size=(2, 2))(x) #change shape -> 16 x 16 x 64

    #more complicated shapes 64 -> 128
    x = layers.Conv2D(
        filters=128,
        kernel_size=(3, 3),
        activation="relu",
        padding="same",
    )(x)
    x = layers.MaxPooling2D(pool_size=(2, 2))(x) #change shape -> 8 x 8 x 128

    #take average value for feature 8 x 8 x 128 -> 128
    x = layers.GlobalAveragePooling2D()(x)
    #learn all 128 features
    x = layers.Dense(128, activation="relu")(x)

    image_features = x

    #~~~~~~~~~~~~~~~~~~
    # Stroke branch: GRU = Gated Recurrent Unit (sequence)
    #~~~~~~~~~~~~~~~~~~

    stroke_input = layers.Input(shape = stroke_shape, name="stroke_input")

    #return final 64 values to find letter at all 100, 5 -> 64
    s = layers.GRU(
        units=64,
        return_sequences=False, #can be True if searching for all points (100, 64)
        name="stroke_gru"
    )(stroke_input)

    s = layers.Dense(128, activation="relu")(s) #shape 64 -> 128

    stroke_features = s

    #~~~~~~~~~~~~~~~~~~
    # Fusion = Combine two branches
    #~~~~~~~~~~~~~~~~~~

    #combine img and stroke = 128 + 128 = 256
    combined = layers.Concatenate(name="fusion")([image_features, stroke_features])

    #learn model by img+stroke combinations
    z = layers.Dense(256, activation="relu")(combined)
    #turn off 30% of neurons to prevent overfiring
    z = layers.Dropout(0.3)(z)

    z = layers.Dense(128, activation="relu")(z)
    #closer to output dropout ,lower
    z = layers.Dropout(0.2)(z)

    #final result layer
    output = layers.Dense(num_classes, activation="linear", name="class_output",)(z)

    #Sequential - for simple, Model - for difficult for Functional API - Model(inputs=..., outputs=...)
    model = Model(
        inputs={
            "image_input": image_input,
            "stroke_input": stroke_input,
        },
        outputs=output,
        name="hybrid_handwriting_model",
    )

    return model

if __name__ == "__main__":
    model = build_hybrid_model(num_classes=52)
    model.summary()