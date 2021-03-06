# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 12:56:34 2019

@author: 14342
"""
# first neural network with keras tutorial
import os
os.chdir('C:\\Users\\14342\\Documents\\GitHub\\Hierarchical-DNN-Activity-Recognition')

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
import pandas as pd
import numpy as np
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.metrics import f1_score
from Extrasensory_Manipulation import *
from Inputs_HDLAct import *
import glob
import os
from sklearn.metrics import f1_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import balanced_accuracy_score

# - data that is passed should have all the labels (parent and child level) ready
def data_cleaner(dataset, feature_set_range, parent_labels, child_labels=None):
    """This function cleans the data given to it and produced X and y for the
    parent and child levels that can be used to train classifiers.
    
    Inpout:
        featur_set_range[list]: the column indices of features to be used for our models
        parent_labels[list]: list of the parent labels
        child_labels[list of list]: a list of list of the child labels. Each element
                                    is the list of one parent branch
        dataset[pd dataframe]: the dataframe to extract X and y from
    
    Output:
        X_parent[pd dataframe]: features of the parent level model
        y_parent[pd dataframe]: response of the parent level model
        X_child[list(pd dataframe)]: list of the features for the child level models
        y_child[list(pd dataframe)]: list of the responses for the child level models
    """
    
    num_parents = len(parent_labels)       # Number of the classes at parent level
    if child_labels is not None:
        assert len(parent_labels) == len(child_labels)
    
    # Cutting out the features and labels from the entire dataset
    features = dataset.iloc[:,feature_set_range]
    labels = dataset[parent_labels]
    
    # Consider eliminating the for loops
    if child_labels is not None:
        for i in range(num_parents):
            for j in range(len(child_labels[i])):
                labels = pd.concat([labels,dataset[child_labels[i][j]]], axis=1)
    
    # We attach the "features" and "labels" to get the raw data
    raw_data = pd.concat([features,labels],axis=1)
    raw_data = raw_data.dropna()
    
    # We are making sure that we have samples that belong to exactly one class
    # of parent labels at the same time. As the parent labels are chosen so that
    # to be completely exclusive, we expect to get none of such samples
    
    # Parent level:
    raw_data['Parent_Belonging'] = 0   # Number of parent classes a sample belongs to
    
    for i in range(num_parents):
        raw_data['Parent_Belonging'] += (raw_data[parent_labels[i]] == 1)*1
    
    #Child level:
    if child_labels is not None:
        raw_data['Child_Belonging'] = 0    # Number of child classes a sample belongs to

        for i in range(num_parents):
            for j in range(len(child_labels[i])):
                raw_data['Child_Belonging'] += (raw_data[child_labels[i][j]] == 1)*1
        raw_data = raw_data[raw_data['Child_Belonging'] == 1]
        
    raw_data = raw_data[raw_data['Parent_Belonging'] == 1]
    
    
    print('Number of samples remaining after removing missing features and labels: '\
          ,len(raw_data))
    
    # Adding the parent label column to the data
    raw_data['Parent_label_index'] = 0    # The index of the parent class that each sample belongs to
    
    for i in range(num_parents):
        raw_data['Parent_label_index'] += (i+1)*(1*(raw_data[parent_labels[i]] == 1))
    
    raw_data['Parent_label_index'] -= 1

    
    if child_labels is not None:
        raw_data['Child_label_index'] = 0     # The index of the child class that each sample belongs to

        for i in range(num_parents):
            for j in range(len(child_labels[i])):
                raw_data['Child_label_index'] += (j+1)*(1*(raw_data[child_labels[i][j]] == 1))
        raw_data['Child_label_index'] -= 1
        
    
    # Collecting X and y for the training phase of the classifiers
    X_parent = raw_data.iloc[:,feature_set_range]
    X_parent = preprocessing.scale(X_parent, axis=0)
    y_parent = raw_data['Parent_label_index']
    
    if child_labels is not None:
        
        X_child = []
        y_child = []
        for i in range(num_parents):
            dataset_ith_parent = raw_data[raw_data['Parent_label_index'] == i]
            X_child.append(dataset_ith_parent.iloc[:,feature_set_range])
            X_child[i] = preprocessing.scale(X_child[i], axis=0)
            y_child.append(dataset_ith_parent['Child_label_index'])
    
        return(X_parent, y_parent, X_child, y_child)
    else:
        return(X_parent, y_parent)

    ##########################################################################
    #--------------------------| Main Program |------------------------------#
    ##########################################################################

if __name__ == '__main__':
    
    dataset_uuids = readdata_csv(data_dir) #reading all data and storing in "dataset" a DF
    
    uuids = list(dataset_uuids.keys())
    
    #Combining the all users' data to dataset
    dataset = dataset_uuids[uuids[0]]
    
    for i in range(1,len(uuids)):
        dataset = pd.concat([dataset,dataset_uuids[uuids[i]]],axis=0)
    
    sensors_list = sensors()
    
    feature_set_range = [0]
    
    for i in range(len(sensors_to_use)):
        feature_set_range += sensors_list[sensors_to_use[i]]
    f1_accuracy = {}
    BA_accuracy = {}
    accuracy = {}
    ##########################################################################
    #-----------------| Stationary vs NonStationary |------------------------#
    ##########################################################################

    #We don't have these labels so we add them by our own Based on the child labels defined
#    parent_labels = ['Stationary','NonStationary']
#    
#    child_labels = [['label:OR_standing','label:SITTING','label:LYING_DOWN'],\
#                    ['label:FIX_running','label:FIX_walking','label:BICYCLING']]
#    
#       
#    dataset['Stationary'] = np.logical_or(dataset['label:OR_standing'],dataset['label:SITTING'])
#    dataset['Stationary'] = np.logical_or(dataset['Stationary'],dataset['label:LYING_DOWN'])*1
#    
#    dataset['NonStationary'] = np.logical_or(dataset['label:FIX_running'],dataset['label:FIX_walking'])
#    dataset['NonStationary'] = np.logical_or(dataset['NonStationary'],dataset['label:BICYCLING'])*1
#
#    
#    X_parent, y_parent, X_child, y_child = data_cleaner(dataset, feature_set_range, parent_labels, child_labels)
#    
    ###########################################################################
    #-------------------------| Indoor vs Outdoor |---------------------------#
    ###########################################################################
    
#    parent_labels = ['label:OR_indoors','label:OR_outside']
#    
#    child_labels = [['label:IN_A_MEETING','label:IN_CLASS','label:AT_HOME'],\
#                    ['label:FIX_running','label:FIX_walking','label:BICYCLING']]
#    
#    feat = dataset.iloc[:,feature_set_range]
#    response = pd.DataFrame()
#    for i in range(len(parent_labels)):
#        for j in range(len(child_labels[i])):
#            response = pd.concat([response,dataset[child_labels[i][j]]], axis=1)
#
#    dataset = pd.concat([feat,response],axis=1)
#    dataset = dataset.dropna()
#    
#    dataset['Stationary'] = np.logical_or(dataset['label:OR_standing'],dataset['label:SITTING'])
#    dataset['Stationary'] = np.logical_or(dataset['Stationary'],dataset['label:LYING_DOWN'])*1
#    
#    dataset['NonStationary'] = np.logical_or(dataset['label:FIX_running'],dataset['label:FIX_walking'])
#    dataset['NonStationary'] = np.logical_or(dataset['NonStationary'],dataset['label:BICYCLING'])*1
#       
#    feature_set_range = range(83)
#    X_parent, y_parent, X_child, y_child = data_cleaner(feature_set_range, parent_labels, child_labels, dataset)
    
    
    ###########################################################################
    #----------------------------| Phone Position |---------------------------#
    ###########################################################################
#    parent_labels = ['label:PHONE_ON_TABLE','label:PHONE_IN_POCKET','label:PHONE_IN_HAND',\
#                     'label:PHONE_IN_BAG']
    
#    parent_labels = ['label:PHONE_IN_BAG','label:PHONE_IN_HAND','label:PHONE_IN_POCKET',\
#                     'label:PHONE_ON_TABLE']
#    
#    child_labels = [['label:PHONE_IN_BAG'],['label:PHONE_IN_HAND'],['label:PHONE_IN_POCKET'],\
#                    ['label:PHONE_ON_TABLE']]
#    
#    feat = dataset.iloc[:,feature_set_range]
#    response = pd.DataFrame()
#    for i in range(len(parent_labels)):
#        for j in range(len(child_labels[i])):
#            response = pd.concat([response,dataset[child_labels[i][j]]], axis=1)
#
#    dataset = pd.concat([feat,response],axis=1)
#    dataset = dataset.dropna()
#    
#    dataset['Stationary'] = np.logical_or(dataset['label:OR_standing'],dataset['label:SITTING'])
#    dataset['Stationary'] = np.logical_or(dataset['Stationary'],dataset['label:LYING_DOWN'])*1
#    
#    dataset['NonStationary'] = np.logical_or(dataset['label:FIX_running'],dataset['label:FIX_walking'])
#    dataset['NonStationary'] = np.logical_or(dataset['NonStationary'],dataset['label:BICYCLING'])*1
#       
#    feature_set_range = range(83)
#    X_parent, y_parent, X_child, y_child = data_cleaner(feature_set_range, parent_labels, child_labels, dataset)
#    feat = dataset.iloc[:,feature_set_range]
#    response = dataset[parent_labels]
#
#    data_to_model = pd.concat([feat,response],axis=1)
#    data_to_model = data_to_model.dropna()
#           
#    feature_set_range = range(83)
#    X_parent, y_parent = data_cleaner(data_to_model, feature_set_range, parent_labels)
#    
#    X_train, X_test, y_train, y_test = train_test_split(X_parent, y_parent, test_size=0.3)
#
#    
#    clf = Sequential()
#    clf.add(Dense(512, input_dim=len(feature_set_range), activation='relu'))
#    clf.add(Dense(128, activation='relu'))
#    clf.add(Dense(6, activation='softmax'))
#    
#    clf.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
#    
#    clf.fit(X_train, y_train, batch_size=100, validation_split=0.2, epochs=100, class_weight='balanced')
#    
#    y_pred = clf.predict_classes(X_test)
#
#    confusion_flat = confusion_matrix(y_test.values, y_pred)
#    
#    f1_accuracy['flat'] = f1_score(y_test.values, y_pred, average='macro')
#    BA_accuracy['flat'] = balanced_accuracy_score(y_test.values, y_pred)
#    accuracy['flat'] = accuracy_score(y_test.values, y_pred)
#
#
#    
#    ###########################################################################
#    #-----------------------| DNN  w/o Hierarchy|-----------------------------#
#    ###########################################################################
    
    parent_labels = ['label:OR_standing','label:SITTING','label:LYING_DOWN',\
                    'label:FIX_running','label:FIX_walking','label:BICYCLING']

    X_parent, y_parent = data_cleaner(dataset, feature_set_range, parent_labels)

    X_train, X_test, y_train, y_test = train_test_split(X_parent, y_parent, test_size=0.3)

    
    clf = Sequential()
    clf.add(Dense(512, input_dim=len(feature_set_range), activation='relu'))
    clf.add(Dense(128, activation='relu'))
    clf.add(Dense(6, activation='softmax'))
    
    clf.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    
    clf.fit(X_train, y_train, batch_size=100, validation_split=0.2, epochs=100, class_weight='balanced')
    
    y_pred = clf.predict_classes(X_test)

    confusion_flat = confusion_matrix(y_test.values, y_pred)
    
    f1_accuracy['flat'] = f1_score(y_test.values, y_pred, average='macro')
    BA_accuracy['flat'] = balanced_accuracy_score(y_test.values, y_pred)
    accuracy['flat'] = accuracy_score(y_test.values, y_pred)
#    
#    ###########################################################################
#    #-----------------------| DNN  with Hierarchy|----------------------------#
#    ###########################################################################
    #We don't have these labels so we add them by our own Based on the child labels defined
#    parent_labels = ['Stationary','NonStationary']
#    
#    child_labels = [['label:OR_standing','label:SITTING','label:LYING_DOWN'],\
#                    ['label:FIX_running','label:FIX_walking','label:BICYCLING']]
#    
#    feat = dataset.iloc[:,feature_set_range]
#    response = pd.DataFrame()
#    for i in range(len(parent_labels)):
#        for j in range(len(child_labels[i])):
#            response = pd.concat([response,dataset[child_labels[i][j]]], axis=1)
#
#    data_to_model = pd.concat([feat,response],axis=1)
#    data_to_model = data_to_model.dropna()
#    
#    data_to_model['Stationary'] = np.logical_or(data_to_model['label:OR_standing'],data_to_model['label:SITTING'])
#    data_to_model['Stationary'] = np.logical_or(data_to_model['Stationary'],data_to_model['label:LYING_DOWN'])*1
#    
#    data_to_model['NonStationary'] = np.logical_or(data_to_model['label:FIX_running'],data_to_model['label:FIX_walking'])
#    data_to_model['NonStationary'] = np.logical_or(data_to_model['NonStationary'],data_to_model['label:BICYCLING'])*1
#       
#    feature_set_range = range(83)
#    X_parent, y_parent, X_child, y_child = data_cleaner(data_to_model, feature_set_range, parent_labels, child_labels)
#
#    X_train, X_test, y_train, y_test = train_test_split(X_parent, y_parent, test_size=0.3)
#
#    #-------------------------------------------------------------------------#
#    clf = Sequential()
#    clf.add(Dense(512, input_dim=len(feature_set_range), activation='relu'))
#    clf.add(Dense(128, activation='relu'))
#    clf.add(Dense(1, activation='sigmoid'))
#    
#    clf.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
#    
#    clf.fit(X_train, y_train, batch_size=100, validation_split=0.2, epochs=100, class_weight='balanced')
#    
#    y_pred = clf.predict_classes(X_test)
#
#    confusion_parent = confusion_matrix(y_test.values, y_pred)
#
#    
#    f1_accuracy['parent'] = f1_score(y_test.values, y_pred, average='macro')
#    BA_accuracy['parent'] = balanced_accuracy_score(y_test.values, y_pred)
#    accuracy['parent'] = accuracy_score(y_test.values, y_pred)
#
#    #-------------------------------------------------------------------------#
#    clf_child = []
#    y_child_pred = []
#    confusion_child = []
#    for i in range(len(parent_labels)):
#        X_train, X_test, y_train, y_test = \
#        train_test_split(X_child[i], y_child[i], test_size=0.3)
#        
#        clf = Sequential()
#        clf.add(Dense(512, input_dim=len(feature_set_range), activation='relu'))
#        clf.add(Dense(128, activation='relu'))
#        clf.add(Dense(len(child_labels[i]), activation='softmax'))
#        
#        clf.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
#        
#        clf.fit(X_train, y_train, batch_size=100, validation_split=0.2, epochs=100, class_weight='balanced')
#        
#        y_pred = clf.predict_classes(X_test)
#
#        confusion_flat = confusion_matrix(y_test.values, y_pred)
#
#        
#        f1_accuracy['child_{}'.format(i)] = f1_score(y_test.values, y_pred, average='macro')
#        BA_accuracy['child_{}'.format(i)] = balanced_accuracy_score(y_test.values, y_pred)
#        accuracy['child_{}'.format(i)] = accuracy_score(y_test.values, y_pred)
#
#
#    
#    ###########################################################################
#   
#    
#    conf_mtrx = confusion_matrix(y_parent_test.values, y_parent_pred.round())
#    
##    df_cm = pd.DataFrame(confusion_matrix, range(2),range(2))
##    plt.figure(figsize = (10,7))
##    sn.set(font_scale=1.4)#for label size
##    sn.heatmap(df_cm, annot=True,annot_kws={"size": 16})# font size
#    f1_score(y_parent_test.values, y_parent_pred.round(), average='macro')
