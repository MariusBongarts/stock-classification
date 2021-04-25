from forecasting.forecast import run
from training.sklearn_models.neural_network import MyNeuralNetwork
from training.sklearn_models.my_ensemble import MyEnsemble

model = MyEnsemble()
run(model)