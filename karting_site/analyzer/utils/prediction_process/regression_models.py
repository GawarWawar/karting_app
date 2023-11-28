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