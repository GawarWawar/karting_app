import pandas as pd
import numpy as np
import requests

import time

import sys
from os.path import dirname, abspath
import importlib.util

from . import coeficient_creation_functions as coef_func
from recorder import models as recorder_models

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
    
    max_temp = df_of_pilots["pilot_temp"].max()
    min_temp = df_of_pilots["pilot_temp"].min()
    temp_from_average_coeficient = (
                coeficient_for_prediction
            *
                (
                    max_temp
                -
                    min_temp
                )
            ) + min_temp
    
    df_with_prediction["temp_from_average_coeficient"] = temp_from_average_coeficient
    
    df_with_prediction = df_with_prediction.merge(
        df_of_karts,
        on="kart"
    )

    return df_with_prediction

def add_kart_column_into_dict_to_return(
    dict_to_process: dict,
    kart_column:pd.Series
):
    for prediction in range(len(dict_to_process["predictions"])):
            dict_to_process_df = pd.DataFrame(dict_to_process["predictions"][prediction])
            dict_to_process_df = dict_to_process_df.round(4)
            dict_to_process_df.insert(
                0,
                "kart",
                kart_column,
            )
            dict_to_process_df = dict_to_process_df.sort_values("kart", ignore_index=True, inplace=False)
            dict_to_process["predictions"][prediction] = dict_to_process_df.to_dict(
                    orient="records",
                    #indent=2
                )
    return dict_to_process

# Used in analyze_race only, but twice
def form_return_after_analyzation_with_error_check (
    dict_with_predictions:dict,
    
    series_of_karts:pd.Series,
    word_to_name_predictions_type:str,
):
    dict_to_return = {}
    try:
        dict_with_predictions["error"]
    except KeyError: 
        dict_to_return.update(
            {
                f"{word_to_name_predictions_type}_r2_scores" : dict_with_predictions["r2_score_values_dict"]
            }
        )

        dict_with_predictions = add_kart_column_into_dict_to_return(
            dict_to_process=dict_with_predictions,
            kart_column=series_of_karts 
        )

        dict_to_return.update(
            {
                f"{word_to_name_predictions_type}_predictions": dict_with_predictions["predictions"]
            }
        )
    else:
        dict_to_return.update(
            {
                f"{word_to_name_predictions_type}_message": dict_with_predictions["message"]
            }
        )

    return dict_to_return