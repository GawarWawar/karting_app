import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.utils.validation import column_or_1d 

#NEEDS TO BE REWORKED INTO CLASS

def standart_scaler_fit_one_dimentional_data_set (
    data_set_to_fit: np.ndarray,
    standard_scaler_instance: StandardScaler
) -> None:
    """
    Fit a one-dimensional data set into a StandardScaler instance.

    This function fits a one-dimensional data set into a provided StandardScaler instance, preparing the scaler
    for later use in transforming similar data sets.

    Parameters:
    - data_set_to_fit (np.ndarray): One-dimensional array-like data set to fit into the scaler.
    - standard_scaler_instance (StandardScaler): Instance of StandardScaler to fit the data into.

    Returns:
    - None: The function modifies the provided StandardScaler instance in-place, and it does not return a value.

    Note:
    The function reshapes the input data set to ensure it is one-dimensional, and then fits the provided
    StandardScaler instance on it. The fitted scaler can be used for transforming similar data sets.
    """
    standard_scaler_instance.fit(
        data_set_to_fit.reshape(
            len(data_set_to_fit), 
            1
        )
    )

def standart_scaler_transform_one_dimentional_data_set (
    data_set_to_transform:np.ndarray,
    standard_scaler_instance: StandardScaler
) -> np.ndarray:
    """
    Transform a one-dimensional data set using a pre-fitted StandardScaler instance.

    This function transforms a one-dimensional data set using a pre-fitted StandardScaler instance,
    applying the same scaling parameters used during the fitting process.

    Parameters:
    - data_set_to_transform (np.ndarray): One-dimensional array-like data set to be transformed.
    - standard_scaler_instance (StandardScaler): Pre-fitted instance of StandardScaler for transforming the data.

    Returns:
    - np.ndarray: Transformed one-dimensional data set.

    Note:
    The function reshapes the input data set to ensure it is one-dimensional and then transforms it
    using the pre-fitted StandardScaler instance. The transformed data set is returned.
    """
    # Reshape the input data set to ensure it is one-dimensional
    data_set_to_transform = data_set_to_transform.reshape(
            len(data_set_to_transform), 
            1
        )
    # Transform the one-dimensional data set using the pre-fitted StandardScaler instance
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
    """
    Inversely transform a one-dimensional data set using a pre-fitted StandardScaler instance.

    This function inversely transforms a one-dimensional data set using a pre-fitted StandardScaler instance,
    applying the inverse of the scaling parameters used during the fitting process.

    Parameters:
    - data_set_to_transform (np.ndarray): One-dimensional array-like data set to be inversely transformed.
    - standard_scaler_instance (StandardScaler): Pre-fitted instance of StandardScaler for inverse transformation.

    Returns:
    - np.ndarray: Inversely transformed one-dimensional data set.

    Note:
    The function applies the inverse transformation to the input data set using the pre-fitted StandardScaler instance.
    The inversely transformed data set is returned.
    """
    return np.ravel(
            standard_scaler_instance.inverse_transform(
                [column_or_1d(data_set_to_transform)]
            )
        )