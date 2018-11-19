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
"""Methods to test model"""

import os
import os.path
import sys
import time
import json

import numpy as np
from keras.models import model_from_json
import matplotlib.pyplot as plt

import autociter.core.pipeline as pipeline

ML_ASSETS_PATH = os.path.dirname(os.path.realpath(__file__)) + '/../../assets/ml'

def running_avg(x, N):
    return np.convolve(x, np.ones((N,))/N)[(N-1):]

def load_model(epoch_id):
    file_path = ML_ASSETS_PATH + '/{0}'.format(epoch_id)
    with open(file_path + '/model_json', 'r') as f:
        json_data = f.read()
        saved_model = model_from_json(json_data)
        saved_model.load_weights(file_path + '/weights')
        return saved_model

def test_model(model, url):
    text = pipeline.get_content_from_url(url)
    vec = pipeline.vectorize_text(text)

    rec = model.predict_proba(np.array([vec]))[0]
    print(sum(rec))

    # plt.imshow(np.array(rec).reshape((30,20)), cmap='hot', interpolation='nearest')
    rec = running_avg(rec, 10)

    print(rec)
    print("\n\n")

    # plt.imshow(np.array(rec).reshape((30,20)), cmap='hot', interpolation='nearest')
    plt.plot(rec)
    plt.axhline(y=np.average(rec), color='r')
    plt.axhline(y=np.average(rec) + np.std(rec), color='b', linestyle='--')
    plt.axhline(y=np.average(rec) + 2*np.std(rec), color='g', linestyle='--')

    top = sorted(rec, key=lambda x: -x)[len(rec)//4]
    
    ret_str = ""
    for i in range(len(rec)):
        ret_str += (text[i] if rec[i] > np.average(rec) + 0.5*np.std(rec) else " ")

    print("Returned String:\n", ret_str)
    return rec

# model = load_model('1541670612')
# model = load_model('1541824433')
# model = load_model('1541847075')
model = load_model('1541922714')

# url = 'https://www.cnn.com/2018/10/12/middleeast/khashoggi-saudi-turkey-recordings-intl/index.html'
url = 'https://www.nytimes.com/2018/11/09/us/politics/matthew-whitaker-acting-attorney-general.html'
# url = 'https://thetab.com/us/uc-berkeley/2017/02/04/honest-packing-list-uc-berkeley-3174'
test_model(model, url)
plt.show()
