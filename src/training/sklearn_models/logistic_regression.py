from sklearn.linear_model import LogisticRegression

from training.sklearn_models.my_sklearn_model import SklearnModel

class MyLogisticRegression(SklearnModel):

  def __init__(self):
    model = LogisticRegression(max_iter=10000)
    super().__init__(model, classifier='logistic_regression')

