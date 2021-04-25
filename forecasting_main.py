from forecasting.forecast import run
from training.sklearn_models.neural_network import MyNeuralNetwork

model = MyNeuralNetwork()
run(model)