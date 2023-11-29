import pandas as pd
import numpy as np
import requests

import time

from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor

from analyzer.utils.analyzation_process import coeficient_creation_functions

def assemble_prediction (
    coeficient_for_prediction: float,
    df_of_pilots: pd.DataFrame,
    df_of_karts: pd.DataFrame,
):
    df_with_prediction = pd.DataFrame(
        {
            "kart": df_of_karts.loc[:, "kart"].drop_duplicates().copy(),
        }
    )
    
    temp_from_average_coeficient = coeficient_creation_functions.make_temp_from_average_coeficient(
        coeficient_for_prediction,
        max_temp=df_of_pilots["pilot_temp"].max(),
        min_temp=df_of_pilots["pilot_temp"].min()
    )
    
    df_with_prediction["temp_from_average_coeficient"] = temp_from_average_coeficient
    
    df_with_prediction = df_with_prediction.merge(
        df_of_karts,
        on="kart"
    )

    return df_with_prediction

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
    list_of_predictions_dict: list[dict],
    predictions: list[list],
    model,
) -> list:
    for prediction_count in range(len(predictions)):
        prediction_to_add = predictions[prediction_count]
        list_of_predictions_dict[prediction_count].update(
            {
                model.__name__  : prediction_to_add
            }
        )
        
    return list_of_predictions_dict