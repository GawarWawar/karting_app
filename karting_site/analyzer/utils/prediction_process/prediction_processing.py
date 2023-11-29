import pandas as pd
import numpy as np
import requests

import time

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler

from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor

from analyzer.utils.analyzation_process import coeficient_creation_functions

def assemble_prediction (
    coeficient_for_prediction: float,
    df_of_pilots: pd.DataFrame,
    df_of_karts: pd.DataFrame,
) -> pd.DataFrame:
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

def add_prediction_to_list_in_dict_form(
    list_of_predictions_dict: list[dict],
    predictions: list[list],
    model: LinearRegression|SVR|DecisionTreeRegressor|RandomForestRegressor,
) -> None:
    for prediction_count in range(len(predictions)):
        list_of_predictions_dict.append({})
        prediction_to_add = predictions[prediction_count]
        list_of_predictions_dict[prediction_count].update(
            {
                model.__name__  : prediction_to_add
            }
        )
        
def encode_and_scale_prediction_data(
    list_of_df_with_predictions: list[pd.DataFrame],
    column_transfoarmer_instance: ColumnTransformer,
    standard_scaler_for_data_to_analyze: StandardScaler
) -> dict:
    dict_to_return = {
        "error": False,
        "message": "", 
        "lists_of_values_to_predict": list()
    }
    # Transforming prediction with Encoder and Feature Scaling
    lists_of_values_to_predict = []
    for df in list_of_df_with_predictions:
        values_to_predict = df.values
        try:
            values_to_predict = column_transfoarmer_instance.transform(values_to_predict)
        except ValueError as error_text:
            print(f"An exception occurred: {str(error_text)}")
            message = "ValueError appeared in prediction transformation process. "
            dict_to_return.update(
                {
                    "error": True,
                    "message": message + str(error_text)+"." 
                }
            )
            return dict_to_return
        try:
            values_to_predict = values_to_predict.toarray()
        except AttributeError:
            pass
        values_to_predict = standard_scaler_for_data_to_analyze.transform(values_to_predict)
        lists_of_values_to_predict.append(values_to_predict)
    
    dict_to_return.update(
        {"lists_of_values_to_predict": lists_of_values_to_predict}
    )
    
    return dict_to_return