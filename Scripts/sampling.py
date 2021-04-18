import pandas as pd
import numpy as np
import time

from sklearn.neighbors import KNeighborsClassifier
from sklearn.neighbors import NearestNeighbors
from random import randrange, uniform
from collections import Counter
from numpy import where

def SMUTE(X_maj, y_maj, n_smute):
    X_maj_prime = X_maj.copy().reset_index(drop=True)
    y_maj_prime = y_maj.copy().reset_index(drop=True)

    x3_y = y_maj_prime.sample().copy()

    knn = NearestNeighbors(n_neighbors=6)

    while((len(X_maj) - len(X_maj_prime)) < n_smute):
        x1_id = X_maj_prime.sample().index.item()
        x1 = X_maj_prime.iloc[x1_id]
        knn.fit(X_maj_prime.to_numpy(), y_maj_prime.to_numpy())
        distances, indices = knn.kneighbors(x1.to_numpy().reshape(1, -1))
        indices = indices[0][1:6]
        x2_id = indices[randrange(5)]
        x2 = X_maj_prime.iloc[x2_id]
        r = uniform(0, 1)
        x3 = x1 + (r * (x2 - x1))

        X_maj_prime = X_maj_prime.drop([x1_id, x2_id]).reset_index(drop=True)
        y_maj_prime = y_maj_prime.drop([x1_id, x2_id]).reset_index(drop=True)

        X_maj_prime = X_maj_prime.append(x3, ignore_index=True)
        y_maj_prime = y_maj_prime.append(x3_y, ignore_index=True)

    return X_maj_prime, y_maj_prime

def SMOTE(X_min, y_min, n_smote):
    X_min = X_min.reset_index(drop=True)
    y_min = y_min.reset_index(drop=True)

    X_min_prime = X_min.copy()
    y_min_prime = y_min.copy()

    x3_y = y_min_prime.sample().copy()

    knn = NearestNeighbors(n_neighbors=6)
    knn.fit(X_min.to_numpy(), y_min.to_numpy())

    while((len(X_min_prime) - len(X_min)) < n_smote):
        x1_id = X_min.sample().index.item()
        x1 = X_min.iloc[x1_id]
        distances, indices = knn.kneighbors(x1.to_numpy().reshape(1, -1))
        indices = indices[0][1:6]
        x2_id = indices[randrange(5)]
        x2 = X_min.iloc[x2_id]
        r = uniform(0, 1)
        x3 = x1 + (r * (x2 - x1))
        X_min_prime = X_min_prime.append(x3, ignore_index=True)
        y_min_prime = y_min_prime.append(x3_y, ignore_index=True)

    return X_min_prime, y_min_prime

def CSMOUTE(majority, minority, ratio):
    X_maj = majority.drop(columns=['is_fraud']).copy()
    y_maj = majority['is_fraud'].copy()

    X_min = minority.drop(columns=['is_fraud']).copy()
    y_min = minority['is_fraud'].copy()

    n = len(X_maj) - len(X_min)
    n_smote = round(n * ratio)
    n_smute = n - n_smote

    X_min_prime, y_min_prime = SMOTE(X_min, y_min, n_smote)
    X_maj_prime, y_maj_prime = SMUTE(X_maj, y_maj, n_smute)

    return X_maj_prime, y_maj_prime, X_min_prime, y_min_prime

meta_data = pd.read_csv("data/meta_features_data.csv", index_col=0)

non_fraud = meta_data[meta_data['is_fraud'] == 0]
fraud = meta_data[meta_data['is_fraud'] == 1]

samples = CSMOUTE(majority=non_fraud, minority=fraud, ratio=0.9)

non_fraud_samples = samples[0]
non_fraud_samples['is_fraud'] = samples[1]
fraud_samples = samples[2]
fraud_samples['is_fraud'] = samples[3]