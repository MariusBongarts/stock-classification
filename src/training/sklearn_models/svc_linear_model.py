from sklearn.neural_network import MLPClassifier
from sklearn_models.my_sklearn_model import SklearnModel
from sklearn.svm import SVC

class MySvcLinearModel(SklearnModel):

  def __init__(self):
    model = SVC(kernel="linear", C=0.025)
    super().__init__(model, classifier='svc_linear_model')

