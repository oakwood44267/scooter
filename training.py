#!/usr/bin/python3

import pandas as pd
import numpy as np
from glob import glob

from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
from sklearn.metrics import classification_report, confusion_matrix

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import *
from tensorflow.keras.utils import to_categorical

# Create Techie Pizza's machine learning model.
# "Default" / initial model achieves about 75% accuracy.
def techie_pizza_model(trainX, trainy):
    n_timesteps, n_features, n_outputs = trainX.shape[1], trainX.shape[2], trainy.shape[1]

    model = Sequential()

    # Input to model
    model.add(Input(shape=(n_timesteps, n_features)))

    ######################################################################################
    # Convolutional layer(s)
    model.add(Conv1D(filters=8, kernel_size=8, activation='relu'))
    model.add(MaxPooling1D(8))      # Usually you follow convolutional layer with pooling
                                    # of size equal to or less than kernel size.
    #model.add(Dropout(0.2))        # Dropout between layers can help prevent overfit
                                    # with limited training data.

    # LSTM layer(s)
    #model.add(LSTM(30, recurrent_dropout=0.2))
    #model.add(Dropout(0.2))
    
    # Flatten before Dense layer(s)
    model.add(Flatten())

    # Dense layer(s)
    #model.add(Dense(36, activation='relu'))
    #model.add(Dropout(0.2))

    ######################################################################################

    # Final layer that predicts which category
    model.add(Dense(n_outputs, activation='softmax'))

    # Build the model.  It is evaluated based on how strongly it predicts the
    # correct category.
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    model.summary()

    return model

# fit and evaluate a model
# from https://machinelearningmastery.com/how-to-develop-rnn-models-for-human-activity-recognition-time-series-classification/
def evaluate_model(trainX, trainy, testX=None, testy=None):
    verbose, batch_size = 1, 32

    model = our_model(trainX, trainy)

    # Train network
    model.fit(trainX, trainy, epochs=epochs, batch_size=batch_size, verbose=verbose)

    # Use trained network to predict hold-back data
    predY = model.predict(testX)
    predy = np.argmax(predY, axis=1)
    comparey = np.argmax(testy, axis=1)

    print('Classification Report')
    print(classification_report(comparey, predy, np.arange(len(categories)), categories))

    # Also use Kera's evaluation function
    loss, accuracy = model.evaluate(testX, testy, batch_size=batch_size, verbose=0)
    return (loss, accuracy)

# run an experiment
# from https://machinelearningmastery.com/how-to-develop-rnn-models-for-human-activity-recognition-time-series-classification/
def run_experiment(trainX, trainy, testX, testy, repeats=7):
    scores = []
    losses = []

    # Repeat experiment
    for r in range(repeats):
        loss, score = evaluate_model(trainX, trainy, testX, testy)
        score = score * 100.0
        print('>#%d: %.3f' % (r+1, score))
        scores.append(score)
        losses.append(loss)

    # Summarize results across experiments
    print(scores)
    print(losses)

    m, s = np.mean(scores), np.std(scores)
    print('Accuracy: %.3f%% (+/-%.3f)' % (m, s))

# from Jupyter notebook written by team
def load_file(filename):
    df = pd.read_csv(filename, names = [ 'time', 'rotx', 'roty', 'rotz', 'accelx', 'accely', 'accelz'])

    # Drop fields we do not care about
    df.drop(columns='time', inplace = True)

    return df

# from Jupyter notebook written by team
def load_label(path):
    loaded = []
    for name in glob(path):
        data = load_file(name)
        loaded.append(data.values)

    return loaded

# Written by Mr. Lyle to format data appropriately for Keras
def load_labels(paths):
    loaded = []
    targets = []

    label = 0

    for path in paths:
        chunk = load_label(path)
        loaded.extend(chunk)
        targets.extend(len(chunk) * [ label ])

        label = label + 1

    loaded = np.asarray(loaded)
    targets = to_categorical(targets)

    return (loaded, targets)

our_model = techie_pizza_model

epochs = 200

# Load labelled data
categories = [ 'Sidewalk', 'Street' ]

X, y = load_labels(['sidewalk/good/*', 'street/good/*'])

# Shuffle the data for better learning
X, y = shuffle(X, y, random_state=640)

# Hold back 20% of the data to measure accuracy
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

run_experiment(X_train, y_train, X_test, y_test)
