"""Simple convnet model architecture."""

import tensorflow as tf
import tensorflow.keras.layers as layers

from enhancerai.tl.zoo.utils import conv_block, dense_block


def simple_convnet(
    input_shape: tuple,
    output_shape: tuple,
    num_conv_blocks: int = 3,
    num_dense_blocks: int = 2,
    residual: int = 0,
    first_activation: str = "exponential",
    activation: str = "swish",
    output_activation: str = "softplus",
    normalization: str = "batch",
    first_filters: int = 192,
    filters: int = 256,
    first_kernel_size: int = 13,
    kernel_size: int = 7,
    first_pool_size: int = 8,
    pool_size: int = 2,
    conv_dropout: float = 0.1,
    dense_dropout: float = 0.3,
    flatten: bool = True,
    dense_size: int = 256,
    bottleneck: int = 8,
) -> tf.keras.Model:
    """
    Construct a Simple ConvNet with standard convolutional and dense blocks.

    Used as a baseline model for regression or classification tasks.

    Parameters
    ----------
    input_shape
        Shape of the input data.
    output_shape
        Shape of the output data.
    num_conv_blocks
        Number of convolutional blocks.
    num_dense_blocks
        Number of dense blocks.
    residual
        Whether to use residual connections.
    first_activation
        Activation function for the first convolutional block.
    activation
        Activation function for subsequent convolutional and dense blocks.
    output_activation
        Activation function for the output layer.
    normalization
        Type of normalization ('batch' or 'layer').
    first_filters
        Number of filters in the first convolutional block.
    filters
        Number of filters in subsequent convolutional blocks.
    first_kernel_size
        Size of the kernel in the first convolutional block.
    kernel_size
        Size of the kernel in subsequent convolutional blocks.
    first_pool_size
        Size of the pooling kernel in the first convolutional block.
    pool_size
        Size of the pooling kernel in subsequent convolutional blocks.
    conv_dropout
        Dropout rate for the convolutional layers.
    dense_dropout
        Dropout rate for the dense layers.
    flatten
        Whether to flatten the output before dense layers.
    dense_size
        Number of neurons in the dense layers.
    bottleneck
        Size of the bottleneck layer.

    Returns
    -------
    tf.keras.Model
        A TensorFlow Keras model.
    """
    output_len, num_tasks = output_shape
    inputs = layers.Input(shape=input_shape, name="sequence")

    x = conv_block(
        inputs,
        filters=first_filters,
        kernel_size=first_kernel_size,
        pool_size=first_pool_size,
        activation=first_activation,
        dropout=conv_dropout,
        normalization=normalization,
        res=residual,
    )

    if num_conv_blocks > 1:
        for i in range(1, num_conv_blocks):
            x = conv_block(
                x,
                filters=i * filters,
                kernel_size=kernel_size,
                pool_size=pool_size,
                activation=activation,
                dropout=i * conv_dropout,
                normalization=normalization,
                res=residual,
            )

    if flatten:
        x = layers.Flatten()(x)
    else:
        x = layers.GlobalAveragePooling1D()(x)

    for _ in range(1, num_dense_blocks):
        x = dense_block(
            x,
            dense_size,
            activation,
            dropout=dense_dropout,
            normalization=normalization,
        )

    x = dense_block(
        x,
        output_len * bottleneck,
        activation,
        dropout=dense_dropout,
        normalization=normalization,
    )

    outputs = layers.Dense(num_tasks, activation=output_activation)(x)
    return tf.keras.Model(inputs=inputs, outputs=outputs)