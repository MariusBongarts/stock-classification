from abc import ABC, abstractmethod
from sklearn.metrics import accuracy_score
from training.helper import save_model, load_model, get_train_test_data
from file_name import file_name
from training.evaluation import get_evaluation
X_train, X_test, y_train, y_test, results_target = get_train_test_data()

class SklearnModel(ABC):
  def __init__(self, model, classifier):
    super().__init__()
    self.X_train = X_train
    self.y_train = y_train
    self.X_test = X_test
    self.y_test = y_test
    self.model = model
    self.classifier = classifier
    self.file_name = f'models/{self.classifier}_{file_name}.sav'
    self.threshold = 0.7

  def train(self):
    print(f'Started {self.classifier} training')
    self.model.fit(self.X_train, self.y_train)
    return self.model

  def save(self):
    save_model(model=self.model, file_name=f'{self.file_name}')

  def load(self):
    try:
      return load_model(file_name=f'{self.file_name}')
    except:
      print(f'No trained model available for {self.classifier} model. Call model.train() to create a .sav file.')
      return None

  def get_probas(self, model=None):
    tested_model = self.model if model is None else model
      # preds = model.predict(X_test)
    probas = tested_model.predict_proba(self.X_test)
    return probas

  def get_predictions(self, model=None):
    probas = self.get_probas(model=model)
    # Only buy when probability is above a specific threshold
    preds = (probas[:,1] >= self.threshold).astype(bool) # set probability threshold
    return preds

  def get_accuracy(self, model=None):
    preds = self.get_predictions(model=model)
    # print(preds)
    accuracy = accuracy_score(self.y_test, preds)
    return accuracy

  def save_if_profit_per_share_is_better(self):
    old_model = self.load()
    if (old_model is None):
      return self.save()
    old_evaluation = self.get_evaluation(model=old_model)
    print('Old evaluation: ', old_evaluation)
    new_evaluation = self.get_evaluation()
    print('New evaluation: ', new_evaluation)
    new_profit_per_share = new_evaluation["profit_per_share"]
    old_profit_per_share = old_evaluation["profit_per_share"]
    if (new_profit_per_share > old_profit_per_share):
      print(f'Saved {self.classifier} model because profit per share improved from {old_profit_per_share} to {new_profit_per_share}')
      return self.save()
    print(f'Did not save {self.classifier} model because profit per share decreased from {old_profit_per_share} to {new_profit_per_share}')

  def predict_proba(self, stock):
    proba = self.load().predict_proba(stock)
    return proba[0][1]

  def predict_probas(self, stocks):
    return self.load().predict_proba(stocks)

  # Earned profit per share
  def get_evaluation(self, model=None):
    preds = self.get_predictions(model=model)
    evaluation = get_evaluation(preds=preds,X_test=X_test.copy(),results_target=results_target.copy())
    return evaluation