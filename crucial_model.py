#!/usr/bin/env python3
#
# crucial_model.py

from keras.models import Sequential
from keras.layers import Dense, Input
from sklearn.model_selection import train_test_split
import numpy as np

# Generate dummy data
X = np.random.rand(100, 10)
y = np.zeros((100,))
y[np.where(X[:, 0] > 0.5)] = 1

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define model architecture
model = Sequential([
    Input(shape=(10,)),  # Correct way to set input shape
    Dense(64, activation='relu'),
    Dense(1, activation='sigmoid')  # Output layer for binary classification
])

# Compile model
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Train model
history = model.fit(X_train, y_train, epochs=20, batch_size=32, validation_data=(X_test, y_test))

# Evaluate model
loss, accuracy = model.evaluate(X_test, y_test)
print('Test loss:', loss)
print('Test accuracy:', accuracy)

def confusion_matrix(true_labels, predictions):
    """
    Generate a confusion matrix for binary classification.

    Args:
    true_labels (list or array): True labels of the data.
    predictions (list or array): Predictions returned by the classifier.

    Returns:
    tuple: Returns a tuple (tn, fp, fn, tp) representing the counts of:
           true negatives, false positives, false negatives, and true positives.
    """
    # Initialize the counts
    tn, fp, fn, tp = 0, 0, 0, 0

    for actual, predicted in zip(true_labels, predictions):
        if actual == 0 and predicted == 0:
            tn += 1
        elif actual == 0 and predicted == 1:
            fp += 1
        elif actual == 1 and predicted == 0:
            fn += 1
        elif actual == 1 and predicted == 1:
            tp += 1

    return (tn, fp, fn, tp)

# Make predictions on test set
predictions = model.predict(X_test)
print(predictions)
confusion_mat = confusion_matrix(y_test, predictions)
print('Confusion matrix:\n', confusion_mat)
