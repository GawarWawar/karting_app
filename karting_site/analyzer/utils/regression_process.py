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


from . import tools as u_tools
from . import regression_evaluation as regres_eval


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
    model,
) -> list:
    for prediction_count in range(len(predictions)):
        prediction_to_add = predictions[prediction_count]
        list_of_dict_to_return[prediction_count].update(
            {
                model.__name__  : prediction_to_add
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
      list_of_df_to_predict: list[pd.DataFrame],
      
      minimum_value_to_r2: float = 0
):
    x = df_to_analyze.iloc[:, :-1].values # Matrix of Features
    y = df_to_analyze.iloc[:, -1].values # Depending variable vector

    # Encoding the Independent Variable
    ct = ColumnTransformer(
        transformers=[("encoder", OneHotEncoder(), [0])],
        remainder="passthrough"
    )
    x = ct.fit_transform(x)
    
    # Splitting the dataset into the Training set and Test set
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.15, random_state = 2)
    
    # Feature Scaling
    sc_x = StandardScaler(with_mean=False)
    x_train = sc_x.fit_transform(x_train)
    x_test = sc_x.transform(x_test)
    
    sc_y = StandardScaler()
    y_train = np.ravel(
        sc_y.fit_transform(
            y_train.reshape(len(y_train), 1)
        )
    )
    y_test = np.ravel(
        sc_y.fit_transform(
            y_test.reshape(len(y_test), 1)
        )
    )
    
    # Transforming prediction with Encoder and Feature Scaling
    lists_of_values_to_predict = []
    list_of_dict_to_return = []
    # for i, value_to_transform in enumerate(lists_of_values_to_predict):
    for df in list_of_df_to_predict:
        values_to_predict = df.values
        values_to_predict = ct.transform(values_to_predict).toarray()
        values_to_predict = sc_x.transform(values_to_predict)
        lists_of_values_to_predict.append(values_to_predict)
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

        if r2_score_value >= minimum_value_to_r2:
            list_of_dict_to_return = add_prediction_to_return_dict(
                list_of_dict_to_return,
                predictions,
                model,
            )
        
    return list_of_dict_to_return