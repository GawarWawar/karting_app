import logging
import numpy as np
import pandas as pd
import requests


from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from scipy.sparse import spmatrix

from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor

import time

from . import regression_models
from analyzer.utils.analyzation_process import coeficient_creation_functions

def generate_regression_prediction_input (
    coeficient_for_prediction: float,
    df_of_pilots: pd.DataFrame,
    df_of_karts: pd.DataFrame,
) -> pd.DataFrame:
    """
    Generate a DataFrame for regression prediction input.

    This function creates a DataFrame with prediction input features for regression analysis. 
    The input features include kart information and generated tempo based on the provided coefficient.
    The generated tempo is calculated using the average coefficient and the tempo statistics 
    of pilots, considering the maximum and minimum tempos in the pilot dataset.

    Parameters:
    - coeficient_for_prediction (float): Coefficient for tempo prediction.
    - df_of_pilots (pd.DataFrame): DataFrame containing statistics about pilots, including tempo.
    - df_of_karts (pd.DataFrame): DataFrame containing statistics about karts.

    Returns:
    - pd.DataFrame: DataFrame with features for regression prediction, including kart information and 
      generated tempo.

    Note:
    The function constructs a DataFrame suitable for regression prediction, combining kart information
    with the generated tempo based on the provided coefficient and pilot tempo statistics.
    """
    # Create a DataFrame to store prediction input features with kart information
    df_with_prediction = pd.DataFrame(
        {
            "kart": df_of_karts.loc[:, "kart"].drop_duplicates().copy(),
        }
    )
    
    # Calculate the tempo from the average coefficient
    temp_from_average_coeficient = coeficient_creation_functions.make_temp_from_average_coeficient(
        coeficient_for_prediction,
        max_temp=df_of_pilots["pilot_temp"].max(),
        min_temp=df_of_pilots["pilot_temp"].min()
    )
    
    # Add the calculated tempo to the prediction input DataFrame
    df_with_prediction["temp_from_average_coeficient"] = temp_from_average_coeficient
    
    # Merge the prediction input DataFrame with kart statistics
    df_with_prediction = df_with_prediction.merge(
        df_of_karts,
        on="kart"
    )

    return df_with_prediction

def make_some_predictions (
    regressor: LinearRegression|SVR|DecisionTreeRegressor|RandomForestRegressor,
    lists_of_values_to_predict: list[np.ndarray]
) -> list[np.ndarray]:
    """
    Make predictions using a regression model for multiple sets of input values.

    This function takes a trained regression model (Linear Regression, Support Vector Regression, 
    Decision Tree Regressor, or Random Forest Regressor) and a list of input values to predict. 
    It returns a list of predictions corresponding to each set of input values.

    Parameters:
    - regressor (LinearRegression|SVR|DecisionTreeRegressor|RandomForestRegressor): 
      Trained regression model for making predictions.
    - lists_of_values_to_predict (List[np.ndarray]): List containing multiple sets of input values 
      to predict.

    Returns:
    - List[np.ndarray]: List of predictions for each set of input values.

    Note:
    The function iterates over the provided list of input values and uses the regression model to 
    make predictions for each set of values. The predictions are then appended to a list and returned.
    """
    list_of_predictions = []
    for value_to_predict in lists_of_values_to_predict:
        prediction = regressor.predict(value_to_predict)
        list_of_predictions.append(prediction)
    return list_of_predictions

def incorporate_predictions_into_dict_list(
    list_of_predictions_dict: list[dict],
    predictions: list[np.ndarray],
    model: regression_models.RegressionModel,
) -> None:
    """
    Incorporate regression predictions into a list of dictionaries.

    This function updates a list of dictionaries with regression predictions generated by a specific model. 
    The predictions are incorporated into the dictionaries, each associated with a specific count in the 
    list of predictions.

    Parameters:
    - list_of_predictions_dict (List[Dict]): List of dictionaries to be updated with regression predictions.
    - predictions (List[np.ndarray]): List of regression predictions corresponding to each dictionary in 
      list_of_predictions_dict.
    - model (regression_models.RegressionModel): The regression model used for predictions.

    Returns:
    - None: The function modifies the input list_of_predictions_dict in place.

    Note:
    The function iterates over the provided list_of_predictions_dict and updates each dictionary with 
    predictions from the corresponding list in the 'predictions' input. If the list is longer than 
    list_of_predictions_dict, additional dictionaries are appended to accommodate the extra predictions.
    """
    # Iterate over each prediction count and corresponding prediction list
    for prediction_count, prediction in enumerate(predictions):
        while True:
            # Ensure the predictions list does not exceed the length of the list_of_predictions_dict
            if len(list_of_predictions_dict) < prediction_count + 1:
                # If the prediction count exceeds the existing dictionaries, append a new dictionary  
                list_of_predictions_dict.append({})
            else:
                # Update the dictionary at the current prediction count with the predictions
                list_of_predictions_dict[prediction_count].update(
                    {
                        model.name: prediction
                    }
                )
                # Break the loop once the dictionary has been updated or appended  
                break
        
def encode_prediction_data(
    list_of_df_with_predictions: list[pd.DataFrame],
    column_transfoarmer_instance: ColumnTransformer,
    
    logger_instance: logging.Logger|None = None
) -> dict:
    """
    Encode prediction data using a ColumnTransformer.

    This function takes a list of DataFrames containing prediction data, encodes the categorical features 
    using a provided ColumnTransformer.

    Parameters:
    - list_of_df_with_predictions (List[pd.DataFrame]): List of DataFrames with prediction data.
    - column_transfoarmer_instance (ColumnTransformer): ColumnTransformer instance for encoding features.
    - logger_instance (logging.Logger|None): Optional logger instance for logging warnings.

    Returns:
    - dict: A dictionary containing the encoded lists of values to predict, error flag, 
      and an error message if an exception occurs during the transformation.
      Example: 
      {
          "lists_of_values_to_predict": [array1, array2, ...],
          "error": False,
          "message": ""
      }
    """
    dict_to_return = {
        "lists_of_values_to_predict": [],
        "error": False,
        "message": "", 
    }
    
    # Transforming prediction with Encoder and Feature Scaling
    for df in list_of_df_with_predictions:
        values_to_predict = df.values
        try:
            # Encode categorical features using the provided ColumnTransformer
            values_to_predict = column_transfoarmer_instance.transform(values_to_predict)
        except ValueError as error_text:
            # Handle ValueError exceptions during encoding
            if logger_instance is not None:
                logger_instance.warning(f"An exception occurred: {str(error_text)}")
            message = "ValueError appeared in prediction transformation process. "
            dict_to_return.update(
                {
                    "error": True,
                    "message": message + str(error_text)+"." 
                }
            )
            return dict_to_return
        
        if isinstance(values_to_predict, spmatrix):
            # Convert sparse matrix to dense array if applicable
            values_to_predict = values_to_predict.toarray()
        
        # Scale the data using the provided StandardScaler
        dict_to_return["lists_of_values_to_predict"].append(values_to_predict)
    
    return dict_to_return