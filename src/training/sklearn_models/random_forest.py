from training.sklearn_models.my_sklearn_model import SklearnModel
from sklearn.ensemble import RandomForestClassifier


class MyRandomForest(SklearnModel):

  def __init__(self):
    model = RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1)
    super().__init__(model, classifier='random_forest')

