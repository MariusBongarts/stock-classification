from sklearn.neural_network import MLPClassifier
from training.sklearn_models.my_sklearn_model import SklearnModel
# hidden_layer_sizes=(30,30,30)


class MyNeuralNetwork(SklearnModel):

  def __init__(self):
    model = MLPClassifier(solver='adam', hidden_layer_sizes=(30, 30, 30), max_iter=1000, learning_rate="invscaling")
    super().__init__(model, classifier='neural_network')

