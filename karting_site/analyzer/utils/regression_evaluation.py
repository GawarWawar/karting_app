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
    pass
    #print(f"{r2_score_value} is R^2 score for {regression_name_to_print}")
    
def evaluate_model_perfomance(
    regressor: LinearRegression|SVR|DecisionTreeRegressor|RandomForestRegressor,
    x_test: list,
    y_test: list
):
    y_pred = regressor.predict(x_test)
    r2_score_value = r2_score(y_test, y_pred)
    print_r2_score(
        r2_score_value=r2_score_value,
        regression_name_to_print=regressor.__class__.__name__,
    )
    return r2_score_value

def multiple_linear_regression(
    x_train,
    y_train,
):  
    # Training the Mulltiple Linear Regression model on the Training set
    regressor = LinearRegression()
    regressor.fit(
        x_train,
        y_train
    )
    
    return regressor
    
def support_vector_regression(
    x_train,
    y_train,
):  
    # Training the SVR model on the Training set
    regressor = SVR(kernel = 'rbf')
    y_train = column_or_1d(y_train)
    regressor.fit(x_train, y_train)
    
    return regressor


def decision_tree_regression(
    x_train,
    y_train,
):
    # Training the Decision Tree Regression on the Training set
    regressor = DecisionTreeRegressor(random_state = 0)
    regressor.fit(x_train, y_train)

    return regressor
    
def random_forest_regression(
    x_train,
    y_train,
    number_of_estimators=50
):  
    # Training the Random Forest Regression model on the Training set
    regressor = RandomForestRegressor(
        n_estimators=number_of_estimators,
        random_state=0
    )
    regressor.fit(x_train, y_train)
    
    return regressor
