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