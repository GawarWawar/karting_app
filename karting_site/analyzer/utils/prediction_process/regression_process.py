from collections.abc import Callable
import logging
import numpy as np
from os.path import dirname, abspath
import pandas as pd
import requests
import time
from scipy.sparse import spmatrix

from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split, cross_val_score, KFold, ShuffleSplit, StratifiedKFold
from sklearn.preprocessing  import OneHotEncoder, PolynomialFeatures, StandardScaler
from sklearn.pipeline import make_pipeline, Pipeline
from sklearn.utils.validation import column_or_1d 

from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor

import sys

from . import regression_evaluation
from . import regression_models
from . import prediction_processing
from . import data_preprocessing

def regression_process(
    df_with_whole_data_set: pd.DataFrame,  
    list_of_df_to_predict: list[pd.DataFrame],
    regression_models_instances: list[regression_models.RegressionModel],
    
    logger_instance: logging.Logger|None = None,
    
    minimum_value_to_r2: float = 0,
    
    size_of_test_set: float = 0.15,
    train_test_split_random_state: int = 2,
    set_n_splits: int = 20,
    
    sequence_number_of_columns_to_OHE: list[int] = [0],
    
    how_many_digits_after_period_to_leave_in: int = 4
) -> dict:
    """
    Perform the entire regression process, including data preprocessing, model training,
    and evaluation. Returns predictions and R^2 score values.

    Parameters:
    - df_with_whole_data_set (pd.DataFrame): DataFrame containing the entire dataset.
    - list_of_df_to_predict (list[pd.DataFrame]): List of DataFrames to make predictions on.
    - regression_models_instances (list[regression_models.RegressionModel]): List of regression model instances.
    - logger_instance (logging.Logger|None): Optional logger for recording process information.
    - minimum_value_to_r2 (float): Minimum R^2 score threshold for considering the model's predictions.
    - size_of_test_set (float): Percentage of the dataset to be used as a test set.
    - train_test_split_random_state (int): Random seed for reproducibility in train-test split.
    - set_n_splits (int): Number of splits for ShuffleSplit.
    - sequence_number_of_columns_to_OHE (list[int]): Sequence numbers of columns to perform One-Hot Encoding.
    - how_many_digits_after_period_to_leave_in (int): Number of digits to round R^2 score to.

    Returns:
    dict: A dictionary containing predictions and R^2 score values or None in case of an error.
    
    Notes:
    - The function performs the following steps:
        1. Extracts features and labels from the dataset.
        2. Applies One-Hot Encoding to categorical columns.
        3. Using Shuffle split, find the best batch of data.
        4. Splits the dataset into training and test sets based on the best batch.
        5. Performs feature scaling on the training and test sets.
        6. Fits a regression model for each specified regression class instance.
        7. Evaluates the models on the test set and makes predictions on additional data entry.
        8. Stores predictions and R^2 score values in a dictionary.

    - The function handles multiple regression models and provides flexibility
      in the choice of models through the 'regression_models_instances' parameter.

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
        remainder="passthrough",
        sparse_threshold=0
    )
    data_to_analyze = column_transformer_instance.fit_transform(data_to_analyze)
            
    shuffler = ShuffleSplit(n_splits = set_n_splits, test_size = size_of_test_set, random_state = train_test_split_random_state)  
    
    # Initializing the operational_dict to store predictions and R^2 score values
    operational_dict = {
        "list_of_predictions_dict": [],
        "r2_score_values_dict": {},
        "r2_score_less_norm_count": 0 
    }
    
    # Looping through each regression model instance
    for model in regression_models_instances:
        
        # Building model for cycle with an integrated model from the list into pipeline
        # Integrate Feature Scaling into model`s pipeline
        cycle_model = regression_models.RegressionModel(
            regressor=make_pipeline(
                StandardScaler(), 
                model.regressor
            ),
            name = model.name
        )
        
        # Finding the best fitting batch of data
        # (basically we are looking for batch that overfits our model)
        accuracies = cross_val_score(
            estimator=cycle_model.regressor,  
            X = data_to_analyze,
            y = answers_to_data,
            cv = shuffler
        )
        
        if accuracies.max() >= 0:
            # Doing log about batch in dubug mode
            logger_instance.debug(
                f"""In {model.name} was choosen {list(accuracies).index(accuracies.max())} shuffle. Score: {accuracies.max():.{how_many_digits_after_period_to_leave_in}}; Accuracy: {accuracies.mean():.{how_many_digits_after_period_to_leave_in}f}; Standard Deviation: {accuracies.std():.{how_many_digits_after_period_to_leave_in}f}."""
            )
            
            the_best_shuffle = list(accuracies).index(accuracies.max())
            
            # Splitting the dataset into the Training set and Test set
            for i, (train_index, test_index) in enumerate(shuffler.split(data_to_analyze, answers_to_data)):
                if i == the_best_shuffle:
                    data_to_analyze_training_set, data_to_analyze_test_set = \
                        data_to_analyze[train_index], data_to_analyze[test_index]
                    answers_to_data_training_set, answers_to_data_test_set = \
                        answers_to_data[train_index], answers_to_data[test_index]  
                    break          
            
            # Training model on data
            cycle_model.regressor.fit(data_to_analyze_training_set, answers_to_data_training_set)
            
            # Preprocessing the predictions' data
            prediction_dict = prediction_processing.encode_prediction_data(
                list_of_df_with_predictions=list_of_df_to_predict,
                column_transfoarmer_instance=column_transformer_instance,
            )
            
            # Checking for errors in the predictions' preprocessing
            if prediction_dict["error"]:
                return prediction_dict
            else:
                lists_of_values_to_predict = \
                    prediction_dict.pop(
                        "lists_of_values_to_predict"
                    )

            # Evaluate the model's performance on the test set
            r2_score_value = regression_evaluation.evaluate_model_perfomance(
                model_regressor= cycle_model.regressor,
                x_test=data_to_analyze_test_set,
                y_test=answers_to_data_test_set,

                logger_instance=logger_instance
            )
            
            
            # Round the R^2 score to the specified number of digits
            r2_score_value = float(f"{r2_score_value:.{how_many_digits_after_period_to_leave_in}f}")

            # Make predictions using the trained model
            predictions = prediction_processing.make_some_predictions(
                regressor=cycle_model.regressor,
                lists_of_values_to_predict=lists_of_values_to_predict
            )


            # Update the operational dictionary with R^2 score and predictions for the current model
            regression_evaluation.update_operational_dict_based_on_r2_score(
                operational_dict=operational_dict,
                this_model_r2_score=r2_score_value,
                min_r2_threshold=minimum_value_to_r2,
                predictions=predictions,
                model=model
            )
            
    
    # Clean up unnecessary variables
    del (
        answers_to_data_test_set,
        answers_to_data_training_set,
        data_to_analyze_test_set,
        data_to_analyze_training_set,
        cycle_model,
        lists_of_values_to_predict,
        minimum_value_to_r2,
        r2_score_value,
        the_best_shuffle,
    )


    # Check if there are statistically significant answers based on the number of models,
    # updates in the operational dictionary accordingly
    if len(regression_models_instances) > operational_dict["r2_score_less_norm_count"]:
        # Add predictions
        dict_to_return = {
            "predictions": operational_dict["list_of_predictions_dict"],
            "r2_score_values_dict": operational_dict["r2_score_values_dict"]
        }
    else:
        # Return an error message
        dict_to_return = {
            "error": True,
            "message": "There weren`t any statistically significant answers" 
        }

    # Clean up remaining variables
    del regression_models_instances, operational_dict
        
    # Log the time taken by the 'regression_process' function if a logger is provided
    if logger_instance is not None:
        end_timer = time.perf_counter()    
        logger_instance.debug(f"{end_timer-start_timer} seconds were taken by 'regression_process'")
    
    return dict_to_return