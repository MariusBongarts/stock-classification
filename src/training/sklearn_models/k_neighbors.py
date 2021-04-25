
from training.sklearn_models.my_sklearn_model import SklearnModel
from sklearn.neighbors import KNeighborsClassifier

class MyKNeighbors(SklearnModel):

  def __init__(self):
    model = KNeighborsClassifier(3)
    super().__init__(model, classifier='k_neighbors')

