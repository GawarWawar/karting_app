import numpy as np
import pandas as pd


def needed_rows(
    df_to_look_for_rows: pd.DataFrame,
    criteries: list
) -> pd.DataFrame:
    """ Finds multiple rows by given criterias

    Args:
        df_to_look_for_rows (pd.DataFrame): DataFrame in which we want to find rows\n
        criteries (list): List of Dictionaries with "column" and "criteria" combination:
            criteries = [{"column":"name_of_a_column", "criteria": criteria_value}]
            Note: programe will do criterias in order, so add them into criteries accordingly

    Returns:
        (list): Returns list of needed indexes
    """
    for criteria in range(len(criteries)):
        df_to_look_for_rows = df_to_look_for_rows[
            df_to_look_for_rows.loc[:,criteries[criteria]["column"]] == \
                criteries[criteria]["criteria"]
        ].copy()
    return df_to_look_for_rows