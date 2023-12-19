import numpy as np
import pandas as pd

import time
import logging

from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import PolynomialFeatures

from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor

from sklearn.metrics import r2_score
from sklearn.utils.validation import column_or_1d 

from . import prediction_processing 
from . import regression_models
    

def evaluate_model_perfomance(
    model_regressor: regression_models.RegressionModel,
    x_test: list,
    y_test: list,
    
    logger_instance: logging.Logger|None = None,
    log_r2_score: bool = False
):
    y_pred = model_regressor.predict(x_test)
    r2_score_value = r2_score(y_test, y_pred)
    if logger_instance is not None and log_r2_score:
        regression_name_to_log = model_regressor.name
        logger_instance.info(
            f"{r2_score_value} is R^2 score for {regression_name_to_log}"
        )
    return r2_score_value

def update_r2_score_values(
        operational_dict: dict,
        current_r2_score: float,
        model: regression_models.RegressionModel
) -> None:
    operational_dict["r2_score_values_dict"].update({
        model.name: current_r2_score
    })

def update_operational_dict_based_on_r2_score(
        operational_dict: dict,
        current_r2_score: float,
        min_r2_threshold: float,
        predictions: list,
        model: regression_models.RegressionModel
) -> dict:
    """
    Evaluate the R2 score against a minimum threshold and update the operational dictionary.

    Parameters:
    - operational_dict (dict): The operational dictionary to be updated.
    - current_r2_score (float): The r2_score to be evaluated.
    - min_r2_threshold (float): The minimum r2_score threshold.
    - predictions (list): The list of predictions.
    - model (regression_models.RegressionModel): The model used for predictions.

    Returns:
    - dict: The updated operational dictionary.
    """
    if current_r2_score >= min_r2_threshold:
        prediction_processing.incorporate_predictions_into_dict_list(
            operational_dict["list_of_predictions_dict"],
            predictions,
            model,
        )
        update_r2_score_values(operational_dict, current_r2_score, model)
    else:
        operational_dict['r2_score_less_norm_count'] += 1

    return operational_dict