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

from . import regression_evaluation
from . import regression_models
from . import prediction_processing


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
    data_to_analyze = df_to_analyze.iloc[:, :-1].values # (x) Matrix of Features
    answers_to_data = df_to_analyze.iloc[:, -1].values # (y) Depending variable vector

    # Encoding the Independent Variable
    column_transformer_instance = ColumnTransformer(
        transformers=[("encoder", OneHotEncoder(), [0])],
        remainder="passthrough"
    )
    data_to_analyze_after = column_transformer_instance.fit_transform(data_to_analyze)
    
    # Splitting the dataset into the Training set and Test set
    data_to_analyze_training_set,\
    data_to_analyze_test_set,\
    answers_to_data_training_set,\
    answers_to_data_test_set = train_test_split(
        data_to_analyze_after, 
        answers_to_data, 
        test_size = 0.15, 
        random_state = 2)
    
    # Feature Scaling
    standard_scaler_for_data_to_analyze = StandardScaler(with_mean=False)
    data_to_analyze_training_set = standard_scaler_for_data_to_analyze.fit_transform(
        data_to_analyze_training_set
    )
    data_to_analyze_test_set = standard_scaler_for_data_to_analyze.transform(
        data_to_analyze_test_set
    )
    
    standard_scaler_for_answers_to_data = StandardScaler()
    answers_to_data_training_set = np.ravel(
        standard_scaler_for_answers_to_data.fit_transform(
            answers_to_data_training_set.reshape(
                len(answers_to_data_training_set), 
                1
            )
        )
    )
    answers_to_data_test_set = np.ravel(
        standard_scaler_for_answers_to_data.transform(
            answers_to_data_test_set.reshape(
                len(answers_to_data_test_set), 
                1
            )
        )
    )
    
    dict_to_return = {}
    # Transforming prediction with Encoder and Feature Scaling
    lists_of_values_to_predict = []
    list_of_predictions_dict = []
    for df in list_of_df_to_predict:
        values_to_predict = df.values
        try:
            values_to_predict = column_transformer_instance.transform(values_to_predict)
        except ValueError as VallErr:
            print(f"An exception occurred: {str(VallErr)}")
            message = "ValueError appeared in prediction transformation process. "
            dict_to_return.update(
                {
                    "error": True,
                    "message": message + str(VallErr)+"." 
                }
            )
            return dict_to_return
        try:
            values_to_predict = values_to_predict.toarray()
        except AttributeError:
            pass
        values_to_predict = standard_scaler_for_data_to_analyze.transform(values_to_predict)
        lists_of_values_to_predict.append(values_to_predict)
        list_of_predictions_dict.append({})
    
    list_of_regression_models = [
        regression_models.multiple_linear_regression,
        regression_models.polinomial_regression,
        regression_models.support_vector_regression,
        regression_models.decision_tree_regression,
        regression_models.random_forest_regression,
    ]
    
    r2_score_less_norm_count = 0
    r2_score_values_dict = {}
    dict_to_return = {
        "error": False,
    }
    for model in list_of_regression_models:
        regressor = train_the_model(
            x_train=data_to_analyze_training_set,
            y_train=answers_to_data_training_set,
            model_to_train=model
        )

        r2_score_value = regression_evaluation.evaluate_model_perfomance(
            model_regressor=regressor,
            x_test=data_to_analyze_test_set,
            y_test=answers_to_data_test_set
        )

        r2_score_value = float(f"{r2_score_value:.4f}")

        predictions = []
        predictions = prediction_processing.make_some_predictions(
            regressor=regressor,
            lists_of_values_to_predict=lists_of_values_to_predict
        )

        # Inversing Feature Scaling for predictions
        for i in range(len(predictions)):
            predictions[i] = np.ravel(
                standard_scaler_for_answers_to_data.inverse_transform(
                    [column_or_1d(predictions[i])]
                )
            )

        if r2_score_value >= minimum_value_to_r2:
            list_of_predictions_dict = prediction_processing.add_prediction_to_return_dict(
                list_of_predictions_dict,
                predictions,
                model,
            )
            r2_score_values_dict.update(
                {
                    model.__name__  : r2_score_value
                }
            )
        else:
            r2_score_less_norm_count += 1
        
    if r2_score_less_norm_count < len(list_of_regression_models):
        dict_to_return = {
            "predictions": list_of_predictions_dict,
            "r2_score_values_dict": r2_score_values_dict
        }
    else:
        dict_to_return.update(
                {
                    "error": True,
                    "message": "There weren`t any statistically significant answers" 
                }
            )
        return dict_to_return
        
    return dict_to_return