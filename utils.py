# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import inspect
import textwrap
import pickle
import streamlit as st

List_datasets = ['CBF','Trace','TwoLeadECG','DodgerLoopWeekend']

def read_dataset(dataset):
    with open('{}.pickle','rb') as handle:
        graph = pickle.load(handle)
    X, y = fetch_ucr_dataset_online(dataset)
    return graph,X,y

def create_graph(graph):
    return None


def fetch_ucr_dataset_online(dataset):
    from aeon.datasets import load_classification
    dataCof = load_classification("Trace")
    X = np.squeeze(dataCof[0], axis=1)
    y = dataCof[1].astype(int)
    return X, y
