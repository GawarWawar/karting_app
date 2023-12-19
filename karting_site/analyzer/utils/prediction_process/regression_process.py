import pandas as pd
import numpy as np
import requests

import time
import logging

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
from . import data_preprocessing

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
    df_with_whole_data_set: pd.DataFrame,  
    list_of_df_to_predict: list[pd.DataFrame],
    
    regression_model_builder_functions: list = [
        regression_models.multiple_linear_regression,
        regression_models.polinomial_regression,
        regression_models.support_vector_regression,
        regression_models.decision_tree_regression,
        regression_models.random_forest_regression,
    ],
    
    logger_instance: logging.Logger|None = None,
    
    minimum_value_to_r2: float = 0,
    
    size_of_test_set: float = 0.15,
    train_test_split_random_state: int = 2,
    
    sequence_number_of_columns_to_OHE: list[int] = [0],
    
    how_many_digits_after_period_to_leave_in: int = 4
):
    start_timer = time.perf_counter()
    
    data_to_analyze = df_with_whole_data_set.iloc[:, :-1].values # (x) Matrix of Features
    answers_to_data = df_with_whole_data_set.iloc[:, -1].values # (y) Depending variable vector
    
    del df_with_whole_data_set

    # Encoding the Independent Variable
    column_transformer_instance = ColumnTransformer(
        transformers=[
            ("encoder", OneHotEncoder(), 
            sequence_number_of_columns_to_OHE)
        ],
        remainder="passthrough"
    )
    data_to_analyze = column_transformer_instance.fit_transform(data_to_analyze)
    
    # Splitting the dataset into the Training set and Test set
    data_to_analyze_training_set,\
    data_to_analyze_test_set,\
    answers_to_data_training_set,\
    answers_to_data_test_set = train_test_split(
        data_to_analyze, 
        answers_to_data, 
        test_size = size_of_test_set, 
        random_state = train_test_split_random_state)
    
    del data_to_analyze, answers_to_data
    
    # Feature Scaling
    standard_scaler_for_data_to_analyze = StandardScaler(with_mean=False)
    
    data_to_analyze_training_set = standard_scaler_for_data_to_analyze.fit_transform(
        data_to_analyze_training_set
    )
    data_to_analyze_test_set = standard_scaler_for_data_to_analyze.transform(
        data_to_analyze_test_set
    )
    
    standard_scaler_for_answers_to_data = StandardScaler()
    data_preprocessing.standart_scaler_fit_one_dimentional_data_set(
        answers_to_data_training_set,
        standard_scaler_for_answers_to_data
    )
    
    answers_to_data_training_set = \
        data_preprocessing.standart_scaler_transform_one_dimentional_data_set(
            answers_to_data_training_set,
            standard_scaler_for_answers_to_data
        )
    answers_to_data_test_set = \
        data_preprocessing.standart_scaler_transform_one_dimentional_data_set(
            answers_to_data_test_set,
            standard_scaler_for_answers_to_data
        )
    
    operational_dict = prediction_processing.encode_and_scale_prediction_data(
        list_of_df_with_predictions=list_of_df_to_predict,
        column_transfoarmer_instance=column_transformer_instance,
        standard_scaler_for_data_to_analyze=standard_scaler_for_data_to_analyze
    )
    
    if operational_dict["error"]:
        return operational_dict
    else:
        lists_of_values_to_predict = \
            operational_dict.pop(
                "lists_of_values_to_predict"
            )
        
    del (
        standard_scaler_for_data_to_analyze,
        list_of_df_to_predict
    )
    
    operational_dict = {
        "list_of_predictions_dict": [],
        "r2_score_values_dict": {},
        "r2_score_less_norm_count": 0 
    }
    for model in regression_model_builder_functions:
        regressor = train_the_model(
            x_train=data_to_analyze_training_set,
            y_train=answers_to_data_training_set,
            model_to_train=model
        )

        r2_score_value = regression_evaluation.evaluate_model_perfomance(
            model_regressor=regressor,
            x_test=data_to_analyze_test_set,
            y_test=answers_to_data_test_set,
            
            logger_instance=logger_instance
        )

        r2_score_value = float(f"{r2_score_value:.{how_many_digits_after_period_to_leave_in}f}")

        predictions = []
        predictions = prediction_processing.make_some_predictions(
            regressor=regressor,
            lists_of_values_to_predict=lists_of_values_to_predict
        )

        # Inversing Feature Scaling for predictions
        for prediction_number in range(len(predictions)):
            predictions[prediction_number] = \
                data_preprocessing.standart_scaler_invers_transform_one_dimentional_data_set(
                    predictions[prediction_number],
                    standard_scaler_for_answers_to_data
                )

        regression_evaluation.update_operational_dict_based_on_r2_score(
            operational_dict=operational_dict,
            current_r2_score=r2_score_value,
            min_r2_threshold=minimum_value_to_r2,
            predictions=predictions,
            model=model
        )
        
        del r2_score_value
    
    del (
        standard_scaler_for_answers_to_data, 
        minimum_value_to_r2,
        lists_of_values_to_predict,
        data_to_analyze_training_set,
        answers_to_data_training_set,
        data_to_analyze_test_set,
        answers_to_data_test_set,
    )

    if operational_dict["r2_score_less_norm_count"] < len(regression_model_builder_functions):
        dict_to_return = {
            "predictions": operational_dict["list_of_predictions_dict"],
            "r2_score_values_dict": operational_dict["r2_score_values_dict"]
        }
    else:
        dict_to_return = {
            "error": True,
            "message": "There weren`t any statistically significant answers" 
        }
    
    del regression_model_builder_functions, operational_dict
        
    if logger_instance is not None:
        end_timer = time.perf_counter()    
        logger_instance.debug(f"{end_timer-start_timer} seconds were taken by 'regression_process'")
    return dict_to_return