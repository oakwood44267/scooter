#!/usr/bin/python3

import pandas as pd
import numpy as np
from glob import glob

from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
from sklearn.metrics import classification_report, confusion_matrix

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import *
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.utils import to_categorical

# Create Techie Pizza's machine learning model.
# "Default" / initial model achieves about 70% accuracy.
def techie_pizza_model(trainX, trainy):
    n_timesteps, n_features, n_outputs = trainX.shape[1], trainX.shape[2], trainy.shape[1]

    model = Sequential()

    # Input to model
    model.add(Input(shape=(n_timesteps, n_features)))

    ######################################################################################
    # Convolutional layer(s)
    model.add(Conv1D(filters=16, kernel_size=12, activation='relu'))
    model.add(MaxPooling1D(12))      # Usually you follow convolutional layer with pooling
                                    # of size equal to or less than kernel size.
    model.add(Dropout(0.15))        # Dropout between layers can help prevent overfit
                                    # with limited training data.
    model.add(Conv1D(filters=16, kernel_size=4, activation='relu'))
    model.add(MaxPooling1D(3))      # Usually you follow convolutional layer with pooling
    model.add(Dropout(0.25))        # Dropout between layers can help prevent overfit
    model.add(Conv1D(filters=24, kernel_size=4, activation='relu'))
    model.add(MaxPooling1D(3))      # Usually you follow convolutional layer with pooling
    model.add(Dropout(0.25))        # Dropout between layers can help prevent overfit
    # LSTM layer(s)
    #model.add(LSTM(30, recurrent_dropout=0.2))
    #model.add(Dropout(0.2))
    
    # Flatten before Dense layer(s)
    model.add(Flatten())

    # Dense layer(s)
   # model.add(Dense(50, activation='relu'))
    #model.add(Dropout(0.3))
    model.add(Dense(60, activation='relu'))
    model.add(Dropout(0.25))
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
def evaluate_model(trainX, trainy, testX, testy):
    model = our_model(trainX, trainy)

    # Train network
    model.fit(trainX, trainy, epochs=epochs, batch_size=batch_size, verbose=verbose,
            validation_data=(testX, testy),
            callbacks=[EarlyStopping(monitor='loss', patience=patience, restore_best_weights=True)])

    # Use trained network to predict hold-back data
    predY = model.predict(testX)

    global predy, comparey

    predy = np.append(predy, np.argmax(predY, axis=1))
    comparey = np.append(comparey, np.argmax(testy, axis=1))

    # Also use Kera's evaluation function
    loss, accuracy = model.evaluate(testX, testy, batch_size=batch_size, verbose=0)
    return (loss, accuracy)

# run an experiment
# from https://machinelearningmastery.com/how-to-develop-rnn-models-for-human-activity-recognition-time-series-classification/
def run_experiment(X, y):
    scores = []
    losses = []

    seed = 42

    # Repeat experiment
    for r in range(repeats):
        # Hold back 20% of the data to measure accuracy
        trainX, testX, trainy, testy = train_test_split(X, y, test_size=0.20, random_state=seed)

        loss, score = evaluate_model(trainX, trainy, testX, testy)
        score = score * 100.0
        print('>#%d: %.3f' % (r+1, score))
        scores.append(score)
        losses.append(loss)

        seed += 1

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

predy = np.empty(0)
comparey = np.empty(0)

epochs = 500
patience = 60
verbose = 1
batch_size = 32
repeats = 14

# Load labelled data
categories = [ 'Sidewalk', 'Street', 'Standing' ]

X, y = load_labels(['sidewalk/good/*', 'street/good/*', 'standing/good/*'])

# Shuffle the data
X, y = shuffle(X, y, random_state=640)

run_experiment(X, y)

print('Classification Report')
print(classification_report(comparey, predy, np.arange(len(categories)), categories, digits=3))
cm = confusion_matrix(comparey, predy)

print(cm)
