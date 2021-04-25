import warnings
warnings.filterwarnings('ignore')
from misc.file_name import file_name
from training.helper import get_train_test_data, get_data
from training.sklearn_models.svc_linear_model import MySvcLinearModel
from training.sklearn_models.random_forest import MyRandomForest
from training.sklearn_models.neural_network import MyNeuralNetwork
from training.sklearn_models.logistic_regression import MyLogisticRegression
from training.sklearn_models.my_ensemble import MyEnsemble

def run():
  models = [
    # MyNeuralNetwork(),
    MyRandomForest(),
    # MyLogisticRegression()
    ]

  estimators = []

  for model in models:
    trained_model = model.train()
    model.save_if_accuracy_is_better()
    estimators.append((model.classifier, trained_model))

  ensemble = MyEnsemble(estimators)
  ensemble.train()
  ensemble.save_if_accuracy_is_better()

  evaluation = ensemble.get_evaluation()
  print(evaluation)


