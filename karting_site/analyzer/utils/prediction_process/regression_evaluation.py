import numpy as np
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import PolynomialFeatures

from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor

from sklearn.metrics import r2_score
from sklearn.utils.validation import column_or_1d 

def print_r2_score(
    r2_score_value :float,
    regression_name_to_print: str
):
    print(f"{r2_score_value} is R^2 score for {regression_name_to_print}")
    
def evaluate_model_perfomance(
    model_regressor: \
        LinearRegression|\
        SVR|\
        DecisionTreeRegressor|\
        RandomForestRegressor,
    x_test: list,
    y_test: list,
    
    r2_score_print:bool = False,
):
    y_pred = model_regressor.predict(x_test)
    r2_score_value = r2_score(y_test, y_pred)
    if r2_score_print:
        print_r2_score(
            r2_score_value=r2_score_value,
            regression_name_to_print=model_regressor.__class__.__name__,
        )
    return r2_score_value