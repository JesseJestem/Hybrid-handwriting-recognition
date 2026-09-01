import numpy as np
import tensorflow as tf

from handwriting.models.hybrid import build_hybrid_model

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#1 Model build test
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def test_hybrid_model_builds():

    model = build_hybrid_model(num_classes = 52)

    assert model is not None

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#2 Forward pass test
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def test_hybrid_model_forward_pass_returns_expected_shape():

    batch_size = 4
    model = build_hybrid_model(num_classes = 52)

    image_batch = np.zeros(
        (batch_size, 64, 64, 1),
        dtype = np.float32,
    )

    stroke_batch = np.zeros(
        (batch_size, 100, 6),
        dtype = np.float32,
    )

    output = model(
        {
            "image_input": image_batch,
            "stroke_input": stroke_batch,
        },
        training = False,
    )

    assert output.shape == (batch_size, 52)
    assert np.all(np.isfinite(output.numpy()))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#3 Model save/load test
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def test_hybrid_model_save_and_load(tmp_path):

    model = build_hybrid_model(num_classes = 52)
    model_path = tmp_path / "model.keras"
    model.save(model_path)
    loaded_model = tf.keras.models.load_model(model_path)

    batch_size = 2
    image_batch = np.zeros(
        (batch_size, 64, 64, 1),
        dtype = np.float32,
    )
    stroke_batch = np.zeros(
        (batch_size, 100, 6),
        dtype = np.float32,
    )

    loaded_output = loaded_model(
        {
            "image_input": image_batch,
            "stroke_input": stroke_batch,
        },
        training = False,
    )
    original_output = model(
        {
            "image_input": image_batch,
            "stroke_input": stroke_batch,
        },
        training = False,
    )


    assert loaded_output.shape == (batch_size, 52)
    assert np.all(np.isfinite(loaded_output.numpy()))
    assert np.allclose(
        original_output.numpy(),
        loaded_output.numpy(),
    )