import os
import pickle
import numpy as np

"""This script implements the functions for reading data.
"""

def load_data(data_dir):
    """Load the CIFAR-10 dataset.

    Args:
        data_dir: A string. The directory where data batches
            are stored.

    Returns:
        x_train: An numpy array of shape [50000, 3072].
            (dtype=np.float32)
        y_train: An numpy array of shape [50000,].
            (dtype=np.int32)
        x_test: An numpy array of shape [10000, 3072].
            (dtype=np.float32)
        y_test: An numpy array of shape [10000,].
            (dtype=np.int32)
    """

    ### YOUR CODE HERE
    pwd_training = os.path.join(data_dir, "training")

    xdata_train, ydata_train = list(), list()
    for file in os.listdir(pwd_training):
        with open(os.path.join(pwd_training, file), 'rb') as f:
            batches = pickle.load(f, encoding='bytes')
            xdata_train.append(np.array(batches[b"data"]))
            ydata_train.append(np.array(batches[b"labels"]))
    x_train, y_train = np.concatenate(xdata_train, axis=0), np.concatenate(ydata_train, axis=0) 

    pwd_testing  = os.path.join(data_dir, "testing")

    xdata_test, ydata_test = list(), list()
    for file in os.listdir(pwd_testing):
        with open(os.path.join(pwd_testing, file), 'rb') as f:
            batches = pickle.load(f, encoding='bytes')
            xdata_test.append(np.array(batches[b"data"]))
            ydata_test.append(np.array(batches[b"labels"]))
    x_test, y_test = np.concatenate(xdata_test, axis=0), np.concatenate(ydata_test, axis=0) 
    ### END CODE HERE

    return x_train, y_train, x_test, y_test


def load_testing_images(data_dir):
    """Load the images in private testing dataset.

    Args:
        data_dir: A string. The directory where the testing images
        are stored.

    Returns:
        x_test: An numpy array of shape [N, 3072].
            (dtype=np.float32)
    """

    ### YOUR CODE HERE
    pwd_private = os.path.join(data_dir, "private")
    x_test = np.load(os.path.join(pwd_private, 'private_test_images_2022.npy'))
    
    print("Verification: shape of the test set is", x_test.shape)
    
    ### END CODE HERE

    return x_test


def train_valid_split(x_train, y_train, train_ratio=0.9):
    """Split the original training data into a new training dataset
    and a validation dataset.

    Args:
        x_train: An array of shape [50000, 3072].
        y_train: An array of shape [50000,].
        train_ratio: A float number between 0 and 1.

    Returns:
        x_train_new: An array of shape [split_index, 3072].
        y_train_new: An array of shape [split_index,].
        x_valid: An array of shape [50000-split_index, 3072].
        y_valid: An array of shape [50000-split_index,].
    """
    
    ### YOUR CODE HERE
    split_index = int(np.multiply(x_train.shape[0], train_ratio))
    
    x_train_new = x_train[:split_index]
    y_train_new = y_train[:split_index]
    x_valid = x_train[split_index:]
    y_valid = y_train[split_index:]
    ### END CODE HERE

    return x_train_new, y_train_new, x_valid, y_valid

