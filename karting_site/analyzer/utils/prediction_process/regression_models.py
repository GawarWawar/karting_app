from collections.abc import Callable
import numpy as np
import pandas as pd

from sklearn.pipeline import make_pipeline, Pipeline
from sklearn.preprocessing import StandardScaler, PolynomialFeatures

from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor

from sklearn.metrics import r2_score
from sklearn.utils.validation import column_or_1d 

class RegressionModel():
    """
    A wrapper class for regression models.

    Parameters:
        - regressor (LinearRegression|SVR|DecisionTreeRegressor|RandomForestRegressor|Pipeline): The regression model or pipeline to be used.
        - name (str): The name of the regression model.

    Attributes:
        regressor (LinearRegression|SVR|DecisionTreeRegressor|RandomForestRegressor|Pipeline): The regression model or pipeline used for prediction.
        name (str): The name of the regression model.
    """
    def __init__ (
        self, 
        regressor: LinearRegression|SVR|DecisionTreeRegressor|RandomForestRegressor|Pipeline, 
        name: str
    ) -> None:
        self.regressor = regressor
        self.name = name

MultipleLinearRegression_ = RegressionModel(
    regressor = LinearRegression(), 
    name = "Linear Regression"
)
"""
A regression model instance using Multiple Linear Regression.

Attributes:
    - regressor (LinearRegression): The Multiple Linear Regression model.
    - name (str): The name of the regression model.
"""

PolinomialRegression_ = RegressionModel(
    regressor = make_pipeline(PolynomialFeatures(2), LinearRegression()),
    name = "Polinomial Regression" 
)
"""
A regression model instance using Polynomial Regression.

Attributes:
    - regressor (Pipeline): The Polynomial Regression model pipeline.
    - name (str): The name of the regression model.
"""

SupportVectorRegression_ = RegressionModel(
    regressor = SVR(kernel = "rbf"),
    name = "Support Vector Regression" 
)
"""
A regression model instance using Support Vector Regression.

Attributes:
    - regressor (SVR): The Support Vector Regression model.
    - name (str): The name of the regression model.
"""

DecisionTreeRegression_ = RegressionModel(
    regressor = DecisionTreeRegressor(random_state=0), 
    name = "Decision Tree Regression"
)
"""
A regression model instance using Decision Tree Regression.

Attributes:
    - regressor (SVR): The Decision Tree Regression model.
    - name (str): The name of the regression model.
"""

RandomForestRegression_ = RegressionModel(
    regressor = RandomForestRegressor(
            n_estimators=50,
            random_state=0,
        ),
    name = "Random Forest Regression"
)
"""
A regression model instance using Random Forest Regression.

Attributes:
    - regressor (SVR): The Random Forest Regression.
    - name (str): The name of the regression model.
"""