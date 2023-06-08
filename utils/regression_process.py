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
) -> list:
    list_of_predictions = []
    for value_to_predict in lists_of_values_to_predict:
        prediction = regressor.predict(value_to_predict)
        list_of_predictions.append(prediction)
    return list_of_predictions

def add_prediction_to_return_dict(
    list_of_dict_to_return: list[dict],
    predictions: list[list],
    r2_score_value: float
) -> list:
    for prediction_count in range(len(predictions)):
        prediction_to_add = predictions[prediction_count]
        list_of_dict_to_return[prediction_count].update(
            {
                r2_score_value: prediction_to_add
            }
        )
        
    return list_of_dict_to_return

def train_the_model(
    x_train: list,
    y_train: list,
    model_to_train: Callable[
        [list, list], 
        LinearRegression|SVR|DecisionTreeRegressor|RandomForestRegressor]
) -> LinearRegression|SVR|DecisionTreeRegressor|RandomForestRegressor:
    regressor = model_to_train(
        x_train,
        y_train
    )
    
    return regressor

def regression_process(
      df_to_analyze: pd.DataFrame,  
      list_of_df_to_predict: list[pd.DataFrame]
):
    x = df_to_analyze.iloc[:, :-1].values # Matrix of Features
    y = df_to_analyze.iloc[:, -1].values # Depending variable vector
    
    lists_of_values_to_predict = []
    for df in list_of_df_to_predict:
        values_to_predict = df.values
        lists_of_values_to_predict.append(values_to_predict)
    
    # Encoding the Independent Variable
    ct = ColumnTransformer(
        transformers=[("encoder", OneHotEncoder(), [0,1])],
        remainder="passthrough"
    )
    x = ct.fit_transform(x).toarray()
    
    # Splitting the dataset into the Training set and Test set
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2, random_state = 0)
    
    # Feature Scaling
    sc_x = StandardScaler()
    x_train = sc_x.fit_transform(x_train)
    x_test = sc_x.transform(x_test)
    
    sc_y = StandardScaler()
    y_train = np.ravel(
        sc_y.fit_transform(
            y_train.reshape(len(y_train), 1)
        )
      
    list_of_dict_to_return = do_prediction_and_add_it_to_the_list(
        x_train,
        y_train,
        x_test,
        y_test,
        type_of_prediction_to_do=make_prediction_in_support_vector_regression,
        lists_of_values_to_predict=list_of_values_to_predict,
        list_of_dict_to_return=list_of_dict_to_return
    )
    y_test = np.ravel(
        sc_y.fit_transform(
            y_test.reshape(len(y_test), 1)
        )
    )
    
    # Transforming prediction with Encoder and Feature Scaling
    for i, value_to_transform in enumerate(lists_of_values_to_predict):
        values_to_predict = ct.transform(value_to_transform).toarray()
        values_to_predict = sc_x.transform(values_to_predict)
        lists_of_values_to_predict[i]=values_to_predict

    list_of_dict_to_return = []
    for df_count in range(len(list_of_df_to_predict)):
        list_of_dict_to_return.append({})
    
    list_of_regression_models = [
        regres_eval.multiple_linear_regression,
        regres_eval.support_vector_regression,
        regres_eval.decision_tree_regression,
        regres_eval.random_forest_regression
    ]
    
    for model in list_of_regression_models:
        regressor = train_the_model(
            x_train=x_train,
            y_train=y_train,
            model_to_train=model
        )

        r2_score_value = regres_eval.evaluate_model_perfomance(
            regressor=regressor,
            x_test=x_test,
            y_test=y_test
        )

        r2_score_value = float(f"{r2_score_value:.4f}")

        predictions = []
        predictions = make_some_predictions(
            regressor=regressor,
            lists_of_values_to_predict=lists_of_values_to_predict
        )

        # Inversing Feature Scaling for predictions
        for i in range(len(predictions)):
            predictions[i] = np.ravel(
                sc_y.inverse_transform(
                    [column_or_1d(predictions[i])]
                )
            )

        if r2_score_value >= 0:
            list_of_dict_to_return = add_prediction_to_return_dict(
                list_of_dict_to_return,
                predictions,
                r2_score_value
            )
        
    return list_of_dict_to_return