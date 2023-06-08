import pandas as pd
import numpy as np
import requests

import time

import sys
from os.path import dirname, abspath
import importlib.util

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing  import OneHotEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor

from sklearn.utils.validation import column_or_1d 


from collections.abc import Callable

if __name__ == "__main__":
    import add_row
    import tools as u_tools
    import regression_evaluation as regres_eval
else:
    spec = importlib.util.spec_from_file_location("add_row", "utils/add_row.py")
    add_row = importlib.util.module_from_spec(spec)
    sys.modules["add_row"] = add_row
    spec.loader.exec_module(add_row)

    spec = importlib.util.spec_from_file_location("u_tools", "utils/tools.py")
    u_tools = importlib.util.module_from_spec(spec)
    sys.modules["u_tools"] = u_tools
    spec.loader.exec_module(u_tools)
    
    spec = importlib.util.spec_from_file_location("regres_eval", "utils/regression_evaluation.py")
    regres_eval = importlib.util.module_from_spec(spec)
    sys.modules["regres_eval"] = regres_eval
    spec.loader.exec_module(regres_eval)

def make_some_predictions (
    regressor: LinearRegression|SVR|DecisionTreeRegressor|RandomForestRegressor,
    lists_of_values_to_predict: list[list]
):
    list_of_predictions = []
    for value_to_predict in lists_of_values_to_predict:
        prediction = regressor.predict(value_to_predict)
        list_of_predictions.append(prediction)
    return list_of_predictions

def add_prediction_to_return_dict(
    list_of_dict_to_return: list[dict],
    predictions: list[list],
    r2_score_value: float
):
    for prediction_count in range(len(predictions)):
        prediction_to_add = predictions[prediction_count]
        list_of_dict_to_return[prediction_count].update(
            {
                r2_score_value: prediction_to_add
            }
        )
        
    return list_of_dict_to_return

def make_prediction_in_multiple_linear_regression(
    x_train: list,
    y_train: list,
    x_test: list,
    y_test: list,
    lists_of_values_to_predict: list[list],
    print_prediction = False,
):
    regressor, r2_score_value = regres_eval.multiple_linear_regression(
        x_train,
        y_train,
        x_test,
        y_test,
        print_prediction,
    )
    
    predictions = make_some_predictions(
            regressor=regressor,
            lists_of_values_to_predict=lists_of_values_to_predict
    )
    
    return predictions, r2_score_value

def make_prediction_in_polinomial_regression(
    x_train: list,
    y_train: list,
    x_test: list,
    y_test: list,
    lists_of_values_to_predict: list[list],
    print_prediction = False,
):
    regressor, r2_score_value, poly_reg = regres_eval.polinomial_regression(
        x_train,
        y_train,
        x_test,
        y_test,
        print_prediction
    )
    
    lists_of_values_to_predict_poly = lists_of_values_to_predict.copy()
    
    for i, value_to_predict in enumerate(lists_of_values_to_predict_poly):
        value_to_predict = poly_reg.transform(value_to_predict)
        lists_of_values_to_predict_poly[i]=value_to_predict
    
    predictions = make_some_predictions(
            regressor=regressor,
            lists_of_values_to_predict=lists_of_values_to_predict_poly
    )
    
    return predictions, r2_score_value

def make_prediction_in_support_vector_regression(
    x_train: list,
    y_train: list,
    x_test: list,
    y_test: list,
    lists_of_values_to_predict: list[list],
    print_prediction = False,
):
    regressor, r2_score_value, sc_x, sc_y = regres_eval.support_vector_regression(
        x_train,
        y_train,
        x_test,
        y_test,
        print_prediction
    )
    
    for i, value_to_predict in enumerate(lists_of_values_to_predict):
        value_to_predict = sc_x.transform(value_to_predict)
        lists_of_values_to_predict[i]=value_to_predict
        
    predictions = make_some_predictions(
            regressor=regressor,
            lists_of_values_to_predict=lists_of_values_to_predict
    )
    
    for i, prediction in enumerate(predictions):
        prediction = sc_y.inverse_transform([prediction])
        predictions[i]=prediction[0] 
    
    return predictions, r2_score_value
    
def make_prediction_in_decision_tree_regression(
    x_train: list,
    y_train: list,
    x_test: list,
    y_test: list,
    lists_of_values_to_predict: list[list],
    print_prediction = False,
):
    regressor, r2_score_value = regres_eval.decision_tree_regression(
        x_train,
        y_train,
        x_test,
        y_test,
        print_prediction,
    )
    
    predictions = make_some_predictions(
            regressor=regressor,
            lists_of_values_to_predict=lists_of_values_to_predict
    )
    
    return predictions, r2_score_value

def make_prediction_in_random_forest_regression(
    x_train: list,
    y_train: list,
    x_test: list,
    y_test: list,
    lists_of_values_to_predict: list[list],
    print_prediction = False,
):
    regressor, r2_score_value = regres_eval.random_forest_regression(
        x_train,
        y_train,
        x_test,
        y_test,
        print_prediction,
    )
    
    predictions = make_some_predictions(
            regressor=regressor,
            lists_of_values_to_predict=lists_of_values_to_predict
    )
    
    return predictions, r2_score_value

def do_prediction_and_add_it_to_the_list(
    x_train: list,
    y_train: list,
    x_test: list,
    y_test: list,
    lists_of_values_to_predict: list[list],
    list_of_dict_to_return: list[dict],
    type_of_prediction_to_do: Callable[[list, list, list, list, bool], tuple],
    print_prediction: bool = False,
):
    predictions, r2_score_value = type_of_prediction_to_do(
        x_train,
        y_train,
        x_test,
        y_test,
        print_prediction = print_prediction,
        lists_of_values_to_predict=lists_of_values_to_predict
    )
    
    for i in range(len(predictions)):
        predictions[i] = predictions[i].tolist()
    
    r2_score_value = f"{r2_score_value:.4f}"
    
    list_of_dict_to_return = add_prediction_to_return_dict(
        list_of_dict_to_return,
        predictions,
        r2_score_value
    )
    return list_of_dict_to_return

def regression_process(
      df_to_analyze: pd.DataFrame,  
      list_of_df_to_predict: list[pd.DataFrame]
):
    x = df_to_analyze.iloc[:, :-1].values # Matrix of Features
    y = df_to_analyze.iloc[:, -1].values # Depending variable vector
    
    list_of_values_to_predict = []
    for df in list_of_df_to_predict:
        values_to_predict = df.values
        list_of_values_to_predict.append(values_to_predict)
    
    # Encoding the Independent Variable
    ct = ColumnTransformer(
        transformers=[("encoder", OneHotEncoder(), [0,1])],
        remainder="passthrough"
    )
    x = ct.fit_transform(x).toarray()
    
    for i, item_to_transform in enumerate(list_of_values_to_predict):
        values_to_predict = ct.transform(item_to_transform).toarray()
        list_of_values_to_predict[i]=values_to_predict
    
    # Splitting the dataset into the Training set and Test set
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2, random_state = 0)
    
    sc_x = StandardScaler()
    sc_y = StandardScaler()
    x_train = sc_x.fit_transform(x_train)
    y_train = y_train.reshape(len(y_train), 1)
    y_train = sc_y.fit_transform(y_train)
    y_train = np.ravel(y_train)
    
    x_test = sc_x.transform(x_test)
    y_test = y_test.reshape(len(y_test), 1)
    y_test = sc_y.fit_transform(y_test)
    y_test = np.ravel(y_test)
    
    print_prediction = False
    
    list_of_dict_to_return = []
    for df_count in range(len(list_of_df_to_predict)):
        list_of_dict_to_return.append({})
    
    list_of_dict_to_return = do_prediction_and_add_it_to_the_list(
        x_train,
        y_train,
        x_test,
        y_test,
        type_of_prediction_to_do=make_prediction_in_multiple_linear_regression,
        lists_of_values_to_predict=list_of_values_to_predict,
        list_of_dict_to_return=list_of_dict_to_return
    )
    
    # list_of_dict_to_return = do_prediction_and_add_it_to_the_list(
    #     x_train,
    #     y_train,
    #     x_test,
    #     y_test,
    #     type_of_prediction_to_do=make_prediction_in_polinomial_regression,
    #     lists_of_values_to_predict=list_of_values_to_predict,
    #     list_of_dict_to_return=list_of_dict_to_return
    # )
    
    list_of_dict_to_return = do_prediction_and_add_it_to_the_list(
        x_train,
        y_train,
        x_test,
        y_test,
        type_of_prediction_to_do=make_prediction_in_support_vector_regression,
        lists_of_values_to_predict=list_of_values_to_predict,
        list_of_dict_to_return=list_of_dict_to_return
    )
    
    list_of_dict_to_return = do_prediction_and_add_it_to_the_list(
        x_train,
        y_train,
        x_test,
        y_test,
        type_of_prediction_to_do=make_prediction_in_decision_tree_regression,
        lists_of_values_to_predict=list_of_values_to_predict,
        list_of_dict_to_return=list_of_dict_to_return
    )
    
    list_of_dict_to_return = do_prediction_and_add_it_to_the_list(
        x_train,
        y_train,
        x_test,
        y_test,
        type_of_prediction_to_do=make_prediction_in_random_forest_regression,
        lists_of_values_to_predict=list_of_values_to_predict,
        list_of_dict_to_return=list_of_dict_to_return
    )
    
    return list_of_dict_to_return