import logging
import numpy as np
import pandas as pd

from sklearn.preprocessing import PolynomialFeatures, StandardScaler

from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor

from sklearn.metrics import r2_score
from sklearn.utils.validation import column_or_1d 

import time

from . import prediction_processing 
from . import regression_models
    

def evaluate_model_perfomance(
    model_regressor: regression_models.RegressionModel,
    x_test: list,
    y_test: list,
    
    logger_instance: logging.Logger|None = None,
    log_r2_score: bool = False
):
    """
    Evaluate the performance of a regression model using R^2 score.

    This function takes a regression model, test data (features and target values), and evaluates the model's
    performance using the R^2 score. Optionally, it can log the R^2 score using a provided logger.

    Parameters:
    - model_regressor (regression_models.RegressionModel): Regression model to evaluate.
    - x_test (list): List of features for testing.
    - y_test (list): List of target values for testing.
    - logger_instance (logging.Logger|None): Optional logger instance for logging R^2 score.
    - log_r2_score (bool): Flag to determine whether to log the R^2 score.

    Returns:
    - float: R^2 score indicating the performance of the regression model.
    """
    y_pred = model_regressor.predict(x_test)
    r2_score_value = r2_score(y_test, y_pred)
    if logger_instance is not None and log_r2_score:
        regression_name_to_log = model_regressor.name
        logger_instance.debug(
            f"{r2_score_value} is R^2 score for {regression_name_to_log}"
        )
    return r2_score_value

def update_operational_dict_based_on_r2_score(
        operational_dict: dict,
        this_model_r2_score: float,
        min_r2_threshold: float,
        predictions: list,
        model: regression_models.RegressionModel
) -> dict:
    """
    Evaluate the R^2 score against a minimum threshold and update the operational dictionary.

    Parameters:
    - operational_dict (dict): The operational dictionary to be updated.
    - this_model_r2_score (float): The R^2 score to be evaluated.
    - min_r2_threshold (float): The minimum R^2 score threshold.
    - predictions (list): The list of predictions.
    - model (regression_models.RegressionModel): The model used for predictions.

    Returns:
    - dict: The updated operational dictionary.

    Note:
    - If the R^2 score of the model meets or exceeds the minimum threshold, the operational dictionary
      is updated with predictions and the R^2 score value. Otherwise, the count of models with R^2 scores
      below the threshold is incremented.
    """
    if this_model_r2_score >= min_r2_threshold:
        prediction_processing.incorporate_predictions_into_dict_list(
            operational_dict["list_of_predictions_dict"],
            predictions,
            model,
        )
        
        # Updates the R^2 score values dictionary in the operational dictionary with a model's score
        operational_dict["r2_score_values_dict"].update({model.name: this_model_r2_score})
    else:
        operational_dict['r2_score_less_norm_count'] += 1

    return operational_dict