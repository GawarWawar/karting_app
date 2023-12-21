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

def regression_process(
    df_with_whole_data_set: pd.DataFrame,  
    list_of_df_to_predict: list[pd.DataFrame],
    regression_class_instances: list[regression_models.RegressionModel],
    
    logger_instance: logging.Logger|None = None,
    
    minimum_value_to_r2: float = 0,
    
    size_of_test_set: float = 0.15,
    train_test_split_random_state: int = 2,
    
    sequence_number_of_columns_to_OHE: list[int] = [0],
    
    how_many_digits_after_period_to_leave_in: int = 4
) -> dict:
    """
    Perform the entire regression process, including data preprocessing, model training,
    and evaluation. Returns predictions and R^2 score values.

    Parameters:
    - df_with_whole_data_set (pd.DataFrame): DataFrame containing the entire dataset.
    - list_of_df_to_predict (list[pd.DataFrame]): List of DataFrames to make predictions on.
    - regression_class_instances (list[regression_models.RegressionModel]): List of regression model instances.
    - logger_instance (logging.Logger|None): Optional logger for recording process information.
    - minimum_value_to_r2 (float): Minimum R^2 score threshold for considering the model's predictions.
    - size_of_test_set (float): Percentage of the dataset to be used as a test set.
    - train_test_split_random_state (int): Random seed for reproducibility in train-test split.
    - sequence_number_of_columns_to_OHE (list[int]): Sequence numbers of columns to perform One-Hot Encoding.
    - how_many_digits_after_period_to_leave_in (int): Number of digits to round R^2 score to.

    Returns:
    dict: A dictionary containing predictions and R^2 score values or None in case of an error.
    
    Notes:
    - The function performs the following steps:
        1. Extracts features and labels from the dataset.
        2. Applies One-Hot Encoding to categorical columns.
        3. Splits the dataset into training and test sets.
        4. Performs feature scaling on the training and test sets.
        5. Fits a regression model for each specified regression class instance.
        6. Evaluates the models on the test set and makes predictions on additional datasets.
        7. Inversely scales the predictions for interpretation.
        8. Stores predictions and R^2 score values in a dictionary.

    - The function handles multiple regression models and provides flexibility
      in the choice of models through the 'regression_class_instances' parameter.

    - The function aims to provide a comprehensive regression analysis and can handle various regression models.
    """
    # Start timer to measure the execution time
    start_timer = time.perf_counter()
    
    # Extract features and target values from the whole dataset
    data_to_analyze = df_with_whole_data_set.iloc[:, :-1].values # (x) Matrix of Features
    answers_to_data = df_with_whole_data_set.iloc[:, -1].values # (y) Depending variable vector
    
    # Deleting the dataframe to free up memory
    del df_with_whole_data_set

    # Encoding the Independent Variable using One-Hot Encoding
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
    
    # Deleting unnecessary variables to free up memory
    del data_to_analyze, answers_to_data
    
    # Feature Scaling 
    standard_scaler_for_data_to_analyze = StandardScaler(with_mean=False)
    
    data_to_analyze_training_set = standard_scaler_for_data_to_analyze.fit_transform(
        data_to_analyze_training_set
    )
    data_to_analyze_test_set = standard_scaler_for_data_to_analyze.transform(
        data_to_analyze_test_set
    )
    
    # Feature Scaling for target values
    standard_scaler_for_answers_to_data = StandardScaler()
    data_preprocessing.standart_scaler_fit_one_dimentional_data_set(
        answers_to_data_training_set,
        standard_scaler_for_answers_to_data
    )
    
    # Transforming target values
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
    
    # Preprocessing the predictions' data
    operational_dict = prediction_processing.encode_and_scale_prediction_data(
        list_of_df_with_predictions=list_of_df_to_predict,
        column_transfoarmer_instance=column_transformer_instance,
        standard_scaler_for_data_to_analyze=standard_scaler_for_data_to_analyze
    )
    
    # Checking for errors in the preprocessing
    if operational_dict["error"]:
        return operational_dict
    else:
        lists_of_values_to_predict = \
            operational_dict.pop(
                "lists_of_values_to_predict"
            )

    # Deleting unnecessary variables to free up memory
    del standard_scaler_for_data_to_analyze, list_of_df_to_predict
    
    # Initializing the operational_dict to store predictions and R^2 score values
    operational_dict = {
        "list_of_predictions_dict": [],
        "r2_score_values_dict": {},
        "r2_score_less_norm_count": 0 
    }
    # Looping through each regression model instance
    for model in regression_class_instances:
        try:
            regressor_trained_on_data = model.train_the_model(
                x_train=data_to_analyze_training_set,
                y_train=answers_to_data_training_set,
            )
        except TypeError as raised_type_error:
            # Handle the case where an incorrect instance is provided in regression_class_instances
            raise TypeError(
                f"""
                {raised_type_error}.
                Make sure that RegressionModel instance is activated. Please give class object into regression_class_instances, not class itself
                """
            )

        # Evaluate the model's performance on the test set
        r2_score_value = regression_evaluation.evaluate_model_perfomance(
            model_regressor=regressor_trained_on_data,
            x_test=data_to_analyze_test_set,
            y_test=answers_to_data_test_set,
            
            logger_instance=logger_instance
        )

        # Round the R^2 score to the specified number of digits
        r2_score_value = float(f"{r2_score_value:.{how_many_digits_after_period_to_leave_in}f}")

        # Make predictions using the trained model
        predictions = prediction_processing.make_some_predictions(
            regressor=regressor_trained_on_data,
            lists_of_values_to_predict=lists_of_values_to_predict
        )

        # Inversing Feature Scaling for predictions
        for prediction_number in range(len(predictions)):
            predictions[prediction_number] = \
                data_preprocessing.standart_scaler_invers_transform_one_dimentional_data_set(
                    predictions[prediction_number],
                    standard_scaler_for_answers_to_data
                )

        # Update the operational dictionary with R^2 score and predictions for the current model
        regression_evaluation.update_operational_dict_based_on_r2_score(
            operational_dict=operational_dict,
            this_model_r2_score=r2_score_value,
            min_r2_threshold=minimum_value_to_r2,
            predictions=predictions,
            model=model
        )
        
        # Clean up the variable holding R^2 score
        del r2_score_value
    
    # Clean up unnecessary variables
    del (
        standard_scaler_for_answers_to_data, 
        minimum_value_to_r2,
        lists_of_values_to_predict,
        data_to_analyze_training_set,
        answers_to_data_training_set,
        data_to_analyze_test_set,
        answers_to_data_test_set,
    )

    # Check if there are statistically significant answers based on the number of models and updates in the operational dictionary
    if len(regression_class_instances) > operational_dict["r2_score_less_norm_count"]:
        dict_to_return = {
            "predictions": operational_dict["list_of_predictions_dict"],
            "r2_score_values_dict": operational_dict["r2_score_values_dict"]
        }
    else:
        # Return an error message if there are no statistically significant answers
        dict_to_return = {
            "error": True,
            "message": "There weren`t any statistically significant answers" 
        }
    
    # Clean up remaining variables
    del regression_class_instances, operational_dict
        
    # Log the time taken by the 'regression_process' function if a logger is provided
    if logger_instance is not None:
        end_timer = time.perf_counter()    
        logger_instance.debug(f"{end_timer-start_timer} seconds were taken by 'regression_process'")
    
    return dict_to_return