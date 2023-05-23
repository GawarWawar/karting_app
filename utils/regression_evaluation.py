import numpy as np
import matplotlib.pyplot as plt
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
    

def multiple_linear_regression(
    x_train,
    y_train,
    x_test,
    y_test,
    print_prediction=False,
):  
    # Training the Mulltiple Linear Regression model on the Training set
    regressor = LinearRegression()
    regressor.fit(
        x_train,
        y_train
    )

    # Predicting the Test set results
    y_pred = regressor.predict(x_test)
    np.set_printoptions(precision=2)
    if print_prediction:
        print(np.concatenate(
            (
                y_pred.reshape(len(y_pred), 1), # This is our prediction
                y_test.reshape(len(y_test), 1), # This is our data from dataset
            ),
            axis=1
        ))
    
    # Evaluating the Model Performance
    
    r2_score_value = r2_score(y_test, y_pred)
    print_r2_score(
        r2_score_value=r2_score_value,
        regression_name_to_print="multiple_linear_regression",
    )
    
    return regressor, r2_score_value
    
def polinomial_regression(
    x_train,
    y_train,
    x_test,
    y_test,
    print_prediction=False,
):  
    # Training the Polynomial Regression model on the Training set
    poly_reg = PolynomialFeatures(degree = 4)
    x_poly = poly_reg.fit_transform(x_train)
    
    regressor = LinearRegression()
    regressor.fit(x_poly, y_train)
    
    # Predicting the Test set results
    y_pred = regressor.predict(poly_reg.transform(x_test))
    np.set_printoptions(precision=2)
    if print_prediction:
        print(np.concatenate(
            (
                y_pred.reshape(len(y_pred), 1), # This is our prediction
                y_test.reshape(len(y_test), 1), # This is our data from dataset
            ),
            axis=1
        ))
    
    # Evaluating the Model Performance
    r2_score_value = r2_score(y_test, y_pred)
    print_r2_score(
        r2_score_value=r2_score_value,
        regression_name_to_print="polinomial_regression",
    )
    
    return regressor, r2_score_value, poly_reg

    
def support_vector_regression(
    x_train,
    y_train,
    x_test,
    y_test,
    print_prediction=False,
):
    # Feature Scaling
    sc_x = StandardScaler()
    sc_y = StandardScaler()
    x_train = sc_x.fit_transform(x_train)
    y_train = y_train.reshape(len(y_train), 1)
    y_train = sc_y.fit_transform(y_train)
    
    # Training the SVR model on the Training set
    regressor = SVR(kernel = 'rbf')
    y_train = column_or_1d(y_train)
    regressor.fit(x_train, y_train)

    # Predicring a Test set result
    y_pred = sc_y.inverse_transform(
        regressor.predict(
            sc_x.transform(x_test)
        ).reshape(-1,1)
    )
    np.set_printoptions(precision=2)
    if print_prediction:
        print(np.concatenate(
            (
                y_pred.reshape(len(y_pred), 1), # This is our prediction
                y_test.reshape(len(y_test), 1), # This is our data from dataset
            ),
            axis=1
        ))

    # Evaluating the Model Performance
    r2_score_value = r2_score(y_test, y_pred)
    print_r2_score(
        r2_score_value=r2_score_value,
        regression_name_to_print="support_vector_regression",
    )
    
    return regressor, r2_score_value, sc_x, sc_y


def decision_tree_regression(
    x_train,
    y_train,
    x_test,
    y_test,
    print_prediction=False,
):
    # Training the Decision Tree Regression on the Training set
    regressor = DecisionTreeRegressor(random_state = 0)
    regressor.fit(x_train, y_train)
    
    # Predicring a Test set result
    y_pred = regressor.predict(x_test)
    np.set_printoptions(precision=2)
    if print_prediction:
        print(np.concatenate(
            (
                y_pred.reshape(len(y_pred), 1), # This is our prediction
                y_test.reshape(len(y_test), 1), # This is our data from dataset
            ),
            axis=1
        ))
    
    # Evaluating the Model Performance
    r2_score_value = r2_score(y_test, y_pred)
    print_r2_score(
        r2_score_value=r2_score_value,
        regression_name_to_print="decision_tree_regression",
    )
    
    return regressor, r2_score_value
    
def random_forest_regression(
    x_train,
    y_train,
    x_test,
    y_test,
    print_prediction=False,
    number_of_estimators=50
):  
    # Training the Random Forest Regression model on the Training set
    regressor = RandomForestRegressor(n_estimators=number_of_estimators,random_state=0)
    regressor.fit(x_train, y_train)

    # Predicring a Test set result
    y_pred = regressor.predict(x_test)
    np.set_printoptions(precision=2)
    if print_prediction:
        print(np.concatenate(
            (
                y_pred.reshape(len(y_pred), 1), # This is our prediction
                y_test.reshape(len(y_test), 1), # This is our data from dataset
            ),
            axis=1
        ))
    
    # Evaluating the Model Performance
    r2_score_value = r2_score(y_test, y_pred)
    print_r2_score(
        r2_score_value=r2_score_value,
        regression_name_to_print="random_forest_regression",
    )
    
    return regressor, r2_score_value
