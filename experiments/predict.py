#!/usr/bin/env python3
#
# predict.py

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Input
import numpy as np
import random

# Function to prepare the data for the LSTM model
def create_dataset(data, n_steps):
    X, y = [], []
    for i in range(len(data) - n_steps):
        seq_x, seq_y = data[i:i + n_steps], data[i + n_steps]
        X.append(seq_x)
        y.append(seq_y)
    return np.array(X), np.array(y)

def generate_random_data(num_points=1440, lower_bound=0, upper_bound=100):
    return [random.uniform(lower_bound, upper_bound) for _ in range(num_points)]

def generate_sine_wave(num_points=1440, sample_rate=44100):
    # Random frequency between 1 Hz and 100 Hz
    frequency = random.uniform(1, 100)
    print(f"Generated frequency: {frequency} Hz")

    # Generate the time values
    t = np.linspace(0, num_points / sample_rate, num_points, endpoint=False)

    # Generate the sine wave
    wave = np.sin(2 * np.pi * frequency * t)

    return wave

# Sample data
#data = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
#data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
#data = generate_random_data()
data = generate_sine_wave()
print(data)
n_steps = 3

# Prepare the data
X, y = create_dataset(data, n_steps)

# Reshape from [samples, timesteps] to [samples, timesteps, features]
n_features = 1
X = X.reshape((X.shape[0], X.shape[1], n_features))

# Define the LSTM model using Input layer
model = Sequential([
    Input(shape=(n_steps, n_features)),  # Defining input shape with Input layer
    LSTM(50, activation='relu'),
    Dense(1)
])

# Compile the model
model.compile(optimizer='adam', loss='mse')

# Fit model
model.fit(X, y, epochs=200, verbose=1)

# Demonstrate prediction

for i in range(10):
    x_input = np.array([10, 20, 30])  # Input data to predict the next number
    print(x_input)
    x_input = x_input.reshape((1, n_steps, n_features))
    print(x_input)
    predicted_number = model.predict(x_input, verbose=0)

    print("Predicted Number:", predicted_number)

