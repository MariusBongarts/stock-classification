from training.sklearn_models.my_sklearn_model import SklearnModel
from sklearn.ensemble import VotingClassifier

class MyEnsemble(SklearnModel):

  def __init__(self, estimators=None):
    model = None
    if estimators is not None:
      model = VotingClassifier(estimators, voting='soft')
    super().__init__(model, classifier='my_ensemble')

