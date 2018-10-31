# Copyright 2018 Balaji Veeramani, Michael Wan
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# Author: Michael Wan <m.wan@berkeley.edu>
"""Module that trains model on data collected by pipeline"""

import re
import json
import time

from termcolor import colored
from sklearn.model_selection import train_test_split

import autociter.core.pipeline as pipeline

RESOURCES_PATH = os.path.dirname(os.path.realpath(__file__)) + '/../../resources'

#To-do define args
def build_model():

def get_x_y(train_data, attribute=""):
    """Given the overall training data (list of dics), get a list of
    x (input) and y (output), which will be the input for the model (x),
    and the supervised learning output (y)"""
    x, y = [], []
    for data_point in train_data:
        if attribute in data_point['locs']:
            x.append(data_point['article_one_hot'])
            # To-do: if attribute is author, do something special because
            # type could be list
            y.append(data_point['locs'][attribute])
    return x, y



def train(num, max_epoch = 50, nfolds = 10, batch_size = 128):
    saved_article_data_PATH = RESOURCES_PATH + '/savedArticleData.dat'
    saved_article_data = pipeline.get_saved_data(saved_article_data_PATH)
    
    article_data = sorted(saved_article_data.values(), key=saved_article_data.get)[:num]
    process_id = int(time.time())

    X, Y = get_x_y(article_data, attribute='title')
    # features = 

    # callbacks = [
    #     EarlyStoppingByLossVal(monitor='val_loss', value=0.00001, verbose=1),
    # ]

    for fold in range(nfolds):
        print(colored("Fold {0}/{1}".format(fold+1, nfolds), "green"))
        x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.25)
        print("Training on {0} pieces of data...".format(len(x_train)))
        print("Building model... (length={0},num_features={1},len(valid_labels)={2}")
        # model = build_model(600, X.__len__(), len(valid_labels))







