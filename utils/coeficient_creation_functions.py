import numpy as np
import pandas as pd

def column_with_lap_time_to_coeficient(
    column_to_transform: pd.Series
):
    max_temp = column_to_transform.max()
    min_temp = column_to_transform.min()
    for temp in range(len(column_to_transform)):
        normilezed_temp =(
            (column_to_transform.loc[temp]-min_temp)
            /
            (max_temp-min_temp)
        )
        normilezed_temp = float(f"{normilezed_temp:.4f}")
        column_to_transform.at[temp] = normilezed_temp
    return column_to_transform