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
import plotly
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import networkx as nx
from plotly.subplots import make_subplots

List_datasets = ['CBF','Trace','TwoLeadECG','DodgerLoopWeekend']
List_datasets_length = {'CBF':31,'Trace':27,'TwoLeadECG':14,'DodgerLoopWeekend':77}

cols = plotly.colors.DEFAULT_PLOTLY_COLORS

@st.cache_data(ttl=3600, max_entries=1, show_spinner=True)
def read_dataset(dataset):
    with open('data/graphs/{}.pickle'.format(dataset),'rb') as handle:
        graph = pickle.load(handle)
    X, y = fetch_ucr_dataset_online(dataset)
    length = List_datasets_length[dataset]
    return graph,X,y,length

@st.cache_data(ttl=3600, max_entries=1, show_spinner=True)
def create_graph(graph):
    G = graph['graph']
    G_nx = nx.DiGraph(graph['graph']['list_edge'])
    pos = nx.nx_agraph.graphviz_layout(G_nx,prog="fdp")
    G_label_0,dict_node_0,edge_size_0 = format_graph_viz(G_nx,G['list_edge'],G['dict_node'])

    list_edge_trace = []
    for i,edge in enumerate(G_nx.edges()):
        edge_trace = go.Scatter(
            x=[pos[edge[0]][0],pos[edge[1]][0]], y=[pos[edge[0]][1],pos[edge[1]][1]],
            line=dict(width=edge_size_0[i], color='#888'),
            hoverinfo='none',
            mode='lines')
        list_edge_trace.append(edge_trace)

    node_x = []
    node_y = []
    node_text = []
    for node in G_nx.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        text=node_text,
        marker=dict(
            size=dict_node_0,
            line_width=1))
    fig = go.Figure(data=list_edge_trace + [node_trace],
        layout=go.Layout(
            height=800,
            plot_bgcolor='rgba(0, 0, 0, 0)',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
        )
    return fig,node_text


def fetch_ucr_dataset_online(dataset):
    path = 'data/timeseries/{}/'.format(dataset)
    train_data = pd.read_csv(path + "{}_TRAIN.tsv".format(dataset),sep='\t',header=None)
    target_train = np.array(train_data[0].values)
    train_data = train_data.drop(0,axis=1)
    train_data = train_data.fillna(0)
    data_train = np.array(train_data.values)
    data_train = (data_train - np.mean(data_train,axis=1,keepdims=True))/(np.std(data_train,axis=1,keepdims=True))

    test_data = pd.read_csv(path + "{}_TEST.tsv".format(dataset),sep='\t',header=None)
    target_test = np.array(test_data[0].values)
    test_data = test_data.drop(0,axis=1)
    test_data = test_data.fillna(0)
    data_test = np.array(test_data.values)
    data_test = (data_test - np.mean(data_test,axis=1,keepdims=True))/(np.std(data_test,axis=1,keepdims=True))
    X = np.concatenate([data_train,data_test],axis=0)
    y = np.concatenate([target_train,target_test],axis=0)
    return X,y

def format_graph_viz(G,list_edge,node_weight):
    edge_size = [] 
    for edge in G.edges():
        edge_size.append(list_edge.count([edge[0],edge[1]]))
    edge_size_b = [float(1+(e - min(edge_size)))/float(1+max(edge_size) - min(edge_size)) for e in edge_size]
    edge_size = [min(e*10,5) for e in edge_size_b]
    dict_node = []
    for node in G.nodes():
        if node != "NULL_NODE":
           dict_node.append(max(5,node_weight[node]*0.01))
        else:
           dict_node.append(5)
    
    return G,dict_node,edge_size

def show_ts(X,y,graph):
    st.markdown("Time series grouped based on the true labels (see [UCR-Archive](https://www.cs.ucr.edu/%7Eeamonn/time_series_data_2018/) for more details. Only 50 first time series are displayed.)")
    trace_ts = []
    fig = make_subplots(rows=1, cols=len(set(y)),subplot_titles=["Class {}".format(i) for i in set(y)])
    x_list = list(range(len(X[0])))
    labels = {lab:i+1 for i,lab in enumerate(set(y))}
    for x,lab in zip(X[:50],y[:50]):
        fig.add_trace(
            go.Scatter(x=x_list, y=x, mode='lines', line_color=(cols[labels[lab]][:-1]+",0.5)").replace("rgb","rgba")),
            row=1, col=labels[lab]
        )
    fig.update_layout(height=500)

    st.markdown("Time series grouped based on the clustering labels of $k$-Graph. You can check the graph on the graph tab for more details. Only 50 first time series are displayed.")
    
    fig_pred = make_subplots(rows=1, cols=len(set(y)),subplot_titles=["Cluster {}".format(i) for i in set(y)])
    x_list = list(range(len(X[0])))
    labels_pred = {lab:i+1 for i,lab in enumerate(set(graph['prediction']))}
    for x,lab,pred in zip(X[:50],y[:50],graph['prediction'][:50]):
        fig_pred.add_trace(
            go.Scatter(x=x_list, y=x, mode='lines', line_color=(cols[labels[lab]][:-1]+",0.5)").replace("rgb","rgba")),
            row=1, col=labels_pred[pred]
        )
    fig_pred.update_layout(height=500,title="ARI: {}".format(adjusted_rand_score(graph['prediction'],y)))
    return fig,fig_pred


def get_node_ts(graph,X,node,length):
    result = []
    current_pos = 0
    
    edge_in_time = graph['graph']['edge_in_time']
    for i,edge in enumerate(graph['graph']['list_edge']):
        if node == edge[0]:
            relative_pos = i-graph['graph']['list_edge_pos'][current_pos]
            pos_in_time = min(
                range(len(edge_in_time[current_pos])), 
                key=lambda j: abs(edge_in_time[current_pos][j]-relative_pos))
            ts = X[int(current_pos),int(pos_in_time):int(pos_in_time+length)]
            ts = ts - np.mean(ts)
            result.append(ts)
        
        if i >= graph['graph']['list_edge_pos'][current_pos+1]:
            current_pos += 1

    mean = np.mean(result,axis=0)
    dev = np.std(result,axis=0)

    mean_trace = go.Scatter(
            x=list(range(length)), y=mean,
            line=dict(width=1, color='#888'),
            hoverinfo='none',
            mode='lines')
    lowerbound_trace = go.Scatter(
            x=list(range(length)), y=mean-dev,
            line=dict(width=1, color='#888'),
            hoverinfo='none',
            mode='lines')
    upperbound_trace = go.Scatter(
            x=list(range(length)), y=mean+dev,
            line=dict(width=1, color='#888'),
            hoverinfo='none',
            fill='tonexty',
            mode='lines')
    
    fig = go.Figure(data=[mean_trace,lowerbound_trace,upperbound_trace],
        layout=go.Layout(
            height=300,
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
        )
    
    return fig,len(result)

