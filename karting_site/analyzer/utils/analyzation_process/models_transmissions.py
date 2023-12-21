import pandas as pd
import numpy as np

import time

from django.db import models
from recorder import models as recorder_models
from analyzer import models as analyzer_models

def collect_model_records_into_DataFrame(
    model: models.Model,
    
    inheritance_id: int,
    column_of_inheritance_id: str,    

    columns_names: list = None,
    purge_models_technical_columns:bool = True
):
    """
    Collect records from a Django model into a DataFrame.

    This function fetches records from a Django model with a specified 'inheritance_id' and
    creates a DataFrame. Optionally, specific column names can be provided, and technical
    columns such as 'id' and column that contain 'inheritance_id' can be purged.

    Parameters:
    - model (models.Model): The Django model from which to collect records.
    - inheritance_id (int): The value of the column used for inheritance.
    - column_of_inheritance_id (str): The name of the column used for inheritance.
    - columns_names (list): Optional list of column names to give the columns in the DataFrame.
    If not specified, columns in the DataFrame will have the same names as in the model.
    - purge_models_technical_columns (bool): If True, remove technical columns like 'id' and
      column that contain 'inheritance_id' from the resulting DataFrame. Default is True.

    Returns:
    - pd.DataFrame: The DataFrame containing records from the specified Django model.

    Note:
    The function uses the 'values_list' method to fetch records from the Django model and
    creates a DataFrame from the records. Optionally, specific column names can be provided,
    and technical columns can be purged if 'purge_models_technical_columns' is set to True.
    """
    if columns_names is None:
        meta = model._meta
        columns_names = [
            field.name for field in meta.fields
        ]
        
    filter_kwargs = {
        f"{column_of_inheritance_id}": inheritance_id
    }
    
    records = model.objects.filter(**filter_kwargs).values_list()
    df_records = pd.DataFrame.from_records(
        records, 
        columns=columns_names
    )
    
    if purge_models_technical_columns:
        # Delete columns from model
        for column in ["id", inheritance_id]:
            if column in df_records.columns:
                df_records.pop(column)
    
    return df_records