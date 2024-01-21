#!/usr/bin/env python3
#
# crucial_model.py

from keras.models import Sequential
from keras.layers import Dense
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix

# Generate dummy data
X = np.random.rand(100, 10)
y = np.zeros((100,))
y[np.where(X[:, 0] > 0.5)] = 1

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define model architecture
model = Sequential()
model.add(Dense(64, activation='relu', input_shape=(10,)))
model.add(Dense(32, activation='relu'))
model.add(Dense(8, activation='softmax'))

# Compile model
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Train model
history = model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_test, y_test))

# Evaluate model
loss, accuracy = model.evaluate(X_test, y_test)
print('Test loss:', loss)
print('Test accuracy:', accuracy)

# Make predictions on test set
predictions = model.predict(X_test)
confusion_mat = confusion_matrix(y_test, predictions)
print('Confusion matrix:\n', confusion_mat)


