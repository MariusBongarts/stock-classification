from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings('ignore')

def get_evaluation(preds, X_test, results_target):

  result = X_test.copy()
  result["results_target"] = results_target
  result['predictions'] = preds

  bought = result[result["predictions"] != 0]
  if (len(bought) == 0):
    return {
    'profit_per_share': -1,
    'total_profit': -1,
    'bought_with_win': 0,
    'bought_with_loss': 0,
    'not_bought_but_was_win': 0,
    }


  def get_profit(x):
      if (x["predictions"] == 1) & (x["results_target"] == 1):
          return 1
      if (x["predictions"] == 1) & (x["results_target"] == 0):
          return -1

  bought['profit'] = bought.apply(lambda x: get_profit(x), axis=1)

  total_profit = bought["profit"].sum()
  profit_per_share = total_profit / len(bought)

  bought_with_win = len(result[(result["predictions"] == 1) & (result["results_target"] == 1)])
  bought_with_loss = len(result[(result["predictions"] == 1) & (result["results_target"] == 0)])
  not_bought_but_was_win = len(result[(result["predictions"] == 0) & (result["results_target"] == 1)])

  return {
    'profit_per_share': profit_per_share,
    'total_profit': total_profit,
    'bought_with_win': bought_with_win,
    'bought_with_loss': bought_with_loss,
    'not_bought_but_was_win': not_bought_but_was_win,
  }