import pandas as pd
import numpy as np
import requests

import time

import sys
from os.path import dirname, abspath
import importlib.util

from . import coeficient_creation_functions as coef_func
from recorder import models as recorder_models

#NEED SOME CHANGES
def add_kart_column_into_dict_to_return(
    dict_to_process: dict,
    kart_column:pd.Series
):
    """
    Add a 'kart' column into a dictionary of predictions.

    This function takes a dictionary containing predictions and adds a 'kart' column
    to each prediction, using the provided kart_column.

    Parameters:
    - dict_to_process (dict): The dictionary containing predictions.
    - kart_column (pd.Series): The Series representing the 'kart' column to be added.

    Returns:
    - dict: The modified dictionary with the 'kart' column added to each prediction.

    Note:
    The input dictionary 'dict_to_process' is expected to have a key "predictions" containing a
    list of dictionaries, each representing a prediction.

    The 'kart_column' Series should have the same length as each prediction.

    The 'kart' column is added to each prediction, and the modified dictionary is returned.
    """
    for prediction in range(len(dict_to_process["predictions"])):
            dict_to_process_df = pd.DataFrame(dict_to_process["predictions"][prediction])
            dict_to_process_df = dict_to_process_df.round(
                4 # ADD ARGUMENT HERE
            )
            dict_to_process_df.insert(
                0, # ADD ARGUMENT HERE
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
    """
    Process a dictionary containing predictions and return a formatted result dictionary.

    This function takes a dictionary containing predictions and processes it to create a result
    dictionary with specific keys based on the content of the input dictionary.

    Parameters:
    - dict_with_predictions (dict): The dictionary containing predictions.
    - series_of_karts (pd.Series): The Series representing the 'kart' column to be added.
    - word_to_name_predictions_type (str): A string representing the type of predictions.

    Returns:
    - dict: The formatted result dictionary.

    Note:
    The input dictionary 'dict_with_predictions' is expected to have keys:
    - "predictions": A list of dictionaries, each representing a prediction.
    - "r2_score_values_dict": A dictionary containing R2 score values.
    or
    - "error": A boolean indicating whether an error occurred during analysis.
    - "message": A string providing additional information about the analysis.

    The 'kart_column' Series should have the same length as each prediction.

    The result dictionary is formatted with keys based on the content of 'dict_with_predictions'.
    """
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