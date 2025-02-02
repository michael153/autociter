# Copyright 2018 Balaji Veeramani, Michael Wan
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#	   http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# Author: Michael Wan <m.wan@berkeley.edu>
"""Methods to train model."""

import os
import os.path
import sys
import time

import numpy as np
import sklearn

from termcolor import colored

from sklearn.model_selection import train_test_split

import tensorflow as tf
import keras
from keras.layers import LSTM, Dense, Dropout
from keras.models import Sequential

import autociter.core.pipeline as pipeline

ASSETS_PATH = os.path.dirname(os.path.realpath(__file__)) + '/../../assets'

config = tf.ConfigProto(device_count={'GPU': 1, 'CPU': 4})
sess = tf.Session(config=config)
keras.backend.set_session(sess)

def build_model(input_length=68, output_dim=600):
    '''Builds a Keras machine learning model
    Takes matrices of size (600, 68)
    Outputs (600,) (Softmax)
    https://stackoverflow.com/questions/48026129/how-to-build-a-keras-model-with-multidimensional-input-and-output
    '''
    model = Sequential()
    # model.add(Embedding(600, 300, input_length=input_length))

    model.add(LSTM(2000, input_shape=(600, input_length), return_sequences=True))

    model.add(Dropout(0.2))
    model.add(LSTM(1600, return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(1200))
    model.add(Dropout(0.2))
    model.add(Dense(800, activation='relu'))
    model.add(Dense(800, activation='tanh'))
    model.add(Dense(output_dim, activation='sigmoid'))

    start = time.time()

    model.compile(
        loss='categorical_crossentropy',
        optimizer='rmsprop',
        metrics=['accuracy'])

    print("Model Compilation Time: ", time.time() - start)
    model.summary()
    print("Inputs: {0}".format(model.input_shape))
    print("Outputs: {0}".format(model.output_shape))
    return model

def get_x_y(train_data, attribute=""):
    """Given the overall training data (list of dics), get a list of
    x (input) and y (output), which will be the input for the model (x),
    and the supervised learning output (y)"""
    x, y = [], []
    for data_point in train_data:
        if attribute in data_point['locs']:
            x.append(np.array(data_point['article_one_hot']))
            # To-do: if attribute is author, do something special because
            # type could be list
            if attribute == 'author':
                authors = data_point['locs']['author']
                hash_map = [0] * len(data_point['article_one_hot'])
                for loc in authors:
                    for i in range(loc[0], loc[1]):
                        hash_map[i] = 1
                y.append(hash_map)
            else:
                print(
                    colored(
                        ">>> Fatal Error: Attribute model not supported yet",
                        "cyan", "on_red"))
                sys.exit()
    return np.array(x), np.array(y)

def train(attribute, num, max_epoch=250, nfolds=10, batch_size=128):
    saved_article_data_path = ASSETS_PATH + '/data/article_data.dat'
    saved_article_data = pipeline.get_saved_data(saved_article_data_path)
    article_data = list(saved_article_data.values())[:num]
    process_id = int(time.time())

    X, Y = get_x_y(article_data, attribute=attribute)

    print("X.shape", X.shape)
    print("Y.shape", Y.shape)

    best_m_auc = 0.0
    print("\n\nStarting model training...\n\n")
    for fold in range(nfolds):
        print(colored("Fold {0}/{1}".format(fold + 1, nfolds), "green"))
        x_train, x_test, y_train, y_test = train_test_split(
            X, Y, test_size=0.25)
        x_train, x_holdout, y_train, y_holdout = train_test_split(
            x_train, y_train, test_size=0.05)
        print("Training on {0} pieces of data...".format(len(x_train)))
        print(
            "Building model... (length={0},num_features={1},len(valid_labels)={2}"
        )
        model = build_model(input_length=68, output_dim=600)
        best_iter = -1
        best_auc = 0.0
        for epoch in range(max_epoch):
            model.fit(
                x_train,
                y_train,
                batch_size=batch_size,
                epochs=10,
                validation_split=0.2)

            t_probs = model.predict_proba(x_holdout)
            t_auc = sklearn.metrics.roc_auc_score(y_holdout.flatten(),
                                                  t_probs.flatten())
            print(
                colored(
                    'Epoch %d: auc = %f (best=%f)\n' % (epoch, t_auc,
                                                        best_auc), "green"))
            if t_auc > best_auc:
                best_auc = t_auc
                best_iter = epoch
            else:
                if (epoch - best_iter) >= 3:
                    break

        probs = model.predict_proba(x_test)
        m_auc = sklearn.metrics.roc_auc_score(y_test.flatten(),
                                              probs.flatten())
        print('\nScore is %f\n' % m_auc)
        if m_auc > best_m_auc:
            best_m_auc = m_auc
            optimal_model = model

    epoch_time = int(time.time())
    new_dir = ASSETS_PATH + "/ml/{0}".format(epoch_time)
    os.mkdir(new_dir)
    optimal_model.save_weights(new_dir + "/weights")
    with open(new_dir + "/model_json", "w") as out:
        out.write(optimal_model.to_json())

    return optimal_model

def simple_train(attribute, num):
    saved_article_data_path = ASSETS_PATH + '/data/article_data.dat'
    saved_article_data = pipeline.get_saved_data(saved_article_data_path)
    article_data = list(saved_article_data.values())[:num]
    process_id = int(time.time())

    X, Y = get_x_y(article_data, attribute=attribute)

    print("X.shape", X.shape)
    print("Y.shape", Y.shape)
    model = build_model(input_length=68, output_dim=600)

    x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.25)
    model.fit(x_train, y_train, batch_size=batch_size, epochs=10, validation_split=0.2)

    probs = model.predict_proba(x_test)
    m_auc = sklearn.metrics.roc_auc_score(y_test.flatten(), probs.flatten())
    print('\nScore is %f\n' % m_auc)

    epoch_time = int(time.time())
    new_dir = ASSETS_PATH + "/ml/{0}".format(epoch_time)
    os.mkdir(new_dir)
    optimal_model.save_weights(new_dir + "/weights")
    with open(new_dir + "/model_json", "w") as out:
        out.write(optimal_model.to_json())

    return optimal_model


# train('author', 6000)
simple_train('author', 10000)
