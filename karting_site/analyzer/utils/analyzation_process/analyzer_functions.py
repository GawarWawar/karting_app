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
    
    temp_from_average_coeficient = coef_func.make_temp_from_average_coeficient(
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