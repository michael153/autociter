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
"""(As of now) Defines methods to convert web-scraped text into one-hot encodings to be passed into a model."""

import os
import json
import re
import sys
import time

import numpy as np
import sklearn

from termcolor import colored
from sklearn.model_selection import train_test_split
from keras.layers.core import *
from keras.models import Sequential
from keras.layers.embeddings import Embedding
from keras.callbacks import Callback

import autociter.core.pipeline as pipeline

RESOURCES_PATH = os.path.dirname(os.path.realpath(__file__)) + '/../../resources'

class early_stop_by_loss_val(Callback):
    def __init__(self, monitor='val_loss', value=0.000005, verbose=0):
        super(Callback, self).__init__()
        self.monitor = monitor
        self.value = value
        self.verbose = verbose

    def on_epoch_end(self, epoch, logs={}):
        current = logs.get(self.monitor)
        if current is None:
            print("*** Warning: Early stopping requires %s available!" % self.monitor)
        if current < self.value:
            if self.verbose > 0:
                print("Epoch %05d: early stopping THR" % epoch)
            self.model.stop_training = True

#To-do define args
def build_model(input_length=68, output_dim=600):
    '''Builds a Keras machine learning model
    Takes matrices of size (600, 68)
    Outputs (600, 2) (Softmax)
    '''
    model = Sequential()
    # model.add(Embedding(600, 300, input_length=input_length))
    model.add(Dense(150, input_dim=600, output_dim=300, activation='sigmoid', kernel_initializer='uniform'))
    model.add(Dense(300, activation='sigmoid', kernel_initializer='uniform'))
    model.add(Dense(150, activation='sigmoid', kernel_initializer='uniform'))
    model.add(Dense(300, activation='sigmoid', kernel_initializer='uniform'))
    model.add(Dense(output_dim=output_dim, activation='softmax', kernel_initializer='uniform'))
    start = time.time()
    model.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=['accuracy'])
    print("Model Compilation Time: ", time.time() - start)
    model.summary()
    print("Inputs: {0}".format(model.input_shape))
    print("Outputs: {0}".format(model.output_shape))
    print("Actual input: {0}".format(Input_train.shape))
    print("Actual output: {0}".format(Labels_train[0].shape))
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
                hash_map = [0]*len(data_point['article_one_hot'])
                for loc in authors:
                    for i in range(loc[0], loc[1]):
                        hash_map[i] = 1
                y.append(hash_map)
            else:
                print(colored(">>> Fatal Error: Attribute model not supported yet", "cyan", "on_red"))
                sys.exit()
    return np.array(x), np.array(y)



def train(num, max_epoch = 50, nfolds = 10, batch_size = 128):
    saved_article_data_PATH = RESOURCES_PATH + '/savedArticleData.dat'
    saved_article_data = pipeline.get_saved_data(saved_article_data_PATH)

    article_data = list(saved_article_data.values())[:num]
    process_id = int(time.time())

    X, Y = get_x_y(article_data, attribute='author')
    print(X.shape)

    callbacks = [
        early_stop_by_loss_val(monitor='val_loss', value=0.00001, verbose=1),
    ]

    best_m_auc = 0.0
    print("\n\nStarting model training...\n\n")
    for fold in range(nfolds):
        print(colored("Fold {0}/{1}".format(fold+1, nfolds), "green"))
        x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.25)
        x_train, x_holdout, y_train, y_holdout = train_test_split(x_train, y_train, test_size=0.05)

        print("Training on {0} pieces of data...".format(len(x_train)))
        print("Building model... (length={0},num_features={1},len(valid_labels)={2}")
        model = build_model(input_length=68, output_dim=600)

        best_iter = -1
        best_auc = 0.0

        for epoch in range(max_epoch):
            model.fit(x_train, y_train, batch_size=batch_size, nb_epoch=1, validation_split=0.05, callbacks=callbacks)
            t_probs = model.predict_proba(x_holdout)
            t_auc = sklearn.metrics.roc_auc_score(y_holdout, t_probs)
            print('Epoch %d: auc = %f (best=%f)' % (ep, t_auc, best_auc))
            if t_auc > best_auc:
                best_auc = t_auc
                best_iter = ep
            else:
                if (ep - best_iter) >= 2:
                    break

        probs = model.predict_proba(x_test)
        m_auc = sklearn.metrics.roc_auc_score(y_test, probs)
        print('\nScore is %f' % m_auc)
        if m_auc > best_m_auc:
            best_m_auc = m_auc
            optimal_model = model


train(40)
