import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.utils.validation import column_or_1d 


def standart_scaler_fit_one_dimentional_data_set (
    data_set_to_fit,
    standard_scaler_instance: StandardScaler
):
    standard_scaler_instance.fit(
        data_set_to_fit.reshape(
            len(data_set_to_fit), 
            1
        )
    )

def standart_scaler_transform_one_dimentional_data_set (
    data_set_to_transform,
    standard_scaler_instance: StandardScaler
):
    data_set_to_transform = data_set_to_transform.reshape(
            len(data_set_to_transform), 
            1
        )
    data_set_to_transform = np.ravel(
        standard_scaler_instance.transform(
            data_set_to_transform
        )
    )
    
    return data_set_to_transform

def standart_scaler_invers_transform_one_dimentional_data_set(
    data_set_to_transform,
    standard_scaler_instance: StandardScaler
):
    return np.ravel(
            standard_scaler_instance.inverse_transform(
                [column_or_1d(data_set_to_transform)]
            )
        )