import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score, accuracy_score, precision_score, recall_score, f1_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from sklearn.cluster import KMeans
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import precision_recall_fscore_support
from sklearn.metrics import mean_squared_error as mse
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_validate
from sklearn.model_selection import train_test_split
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.feature_selection import SelectFromModel
from sklearn.svm import LinearSVC, SVC
from sklearn.ensemble import VotingClassifier
from sklearn.feature_selection import RFECV
import warnings
warnings.filterwarnings('ignore')
from file_name import file_name

from sklearn.preprocessing import MinMaxScaler
from training.helper import get_train_test_data, get_data




# Train Logistic Regression
# print("Logistic Regression")
# lr_model = LogisticRegression()
# lr_model.fit(X_train, y_train)
# probas = lr_model.predict_proba(X_test)

# # Only buy when probability is above a specific threshold
# preds = (probas[:,1] >= 0.5).astype(bool) # set probability threshold

# accuracy = accuracy_score(y_test, preds)
# print(f'Acccuracy: {accuracy}')


# Train SVM Model

# print("Started SVM training")
# from sklearn import svm
# model = svm.SVC(probability=True)
# model.fit(X_train, y_train)
# # preds = model.predict(X_test,probability=)
# # print(preds)

# probas = model.predict_proba(X_test)

# # Only buy when probability is above a specific threshold
# preds = (probas[:,1] >= 0.5).astype(bool) # set probability threshold

# accuracy = accuracy_score(y_test, preds)
# print(f'Acccuracy: {accuracy}')

# svm_model = model
# print("Finished SVM training")

# Train Neural Network



#create a dictionary of our models
# estimators=[('logistic_regression', lr_model), ('random_forest', random_forest), ('neural_network', neural_network), ('svm_model', svm_model)]
# estimators=[('neural_network', neural_network), ('svm_model', svm_model)]
# #create our voting classifier, inputting our models
# ensemble = VotingClassifier(estimators, voting='soft')

# #override ensemble

# #fit model to training data
# ensemble.fit(X_train, y_train)
# #test our model on the test data
# ensemble.score(X_test, y_test)

# probas = ensemble.predict_proba(X_test)


# # Only buy when probability is above a specific threshold
# # preds = (probas[:,1] >= 0.55).astype(bool) # set probability threshold
# accuracy = accuracy_score(y_test, preds)
# print(f'Acccuracy: {accuracy}')

from sklearn_models.svc_linear_model import MySvcLinearModel
from sklearn_models.random_forest import MyRandomForest
from sklearn_models.neural_network import MyNeuralNetwork
from sklearn_models.logistic_regression import MyLogisticRegression
from sklearn_models.my_ensemble import MyEnsemble
models = [
  MyNeuralNetwork(),
  # MyRandomForest(),
  # MyLogisticRegression()
  ]

from sklearn.ensemble import VotingClassifier
estimators = []

for model in models:
  trained_model = model.train()
  model.save_if_profit_per_share_is_better()
  estimators.append((model.classifier, trained_model))

ensemble = MyEnsemble(estimators)
ensemble.train()
ensemble.save_if_profit_per_share_is_better()


