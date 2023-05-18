import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def multiple_linear_regression(
    x_train,
    y_train,
    x_test,
    y_test,
    print_prediction=False,
):
    # DOESNT NEED FEATURE SCALING
    
    # Training the Mulltiple Linear Regression model on the Training set
    from sklearn.linear_model import LinearRegression
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
    from sklearn.metrics import r2_score
    print(r2_score(y_test, y_pred))
    
def polinomial_regression(
    x_train,
    y_train,
    x_test,
    y_test,
    print_prediction=False,
):
    # DOESNT NEED FEATURE SCALING
    
    # Training the Polynomial Regression model on the Training set
    from sklearn.preprocessing import PolynomialFeatures
    from sklearn.linear_model import LinearRegression
    poly_reg = PolynomialFeatures(degree = 4)
    X_poly = poly_reg.fit_transform(x_train)
    regressor = LinearRegression()
    regressor.fit(X_poly, y_train)
    
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
    from sklearn.metrics import r2_score
    print(r2_score(y_test, y_pred))
    
def support_vector_regression(
    x_train,
    y_train,
    x_test,
    y_test,
    print_prediction=False,
):
    # NEEDS FEATURE SCALING

    # Feature Scaling
    from sklearn.preprocessing import StandardScaler
    sc_x = StandardScaler()
    sc_y = StandardScaler()
    x_train = sc_x.fit_transform(x_train)
    y_train = y_train.reshape(len(y_train), 1)
    y_train = sc_y.fit_transform(y_train)
    
    # Training the SVR model on the Training set
    from sklearn.svm import SVR
    regressor = SVR(kernel = 'rbf')
    from sklearn.utils.validation import column_or_1d 
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
    from sklearn.metrics import r2_score
    print(r2_score(y_test, y_pred))

def decision_tree_regression(
    x_train,
    y_train,
    x_test,
    y_test,
    print_prediction=False,
):
    # DOESNT NEED FEATURE SCALING
    
    # Training the Decision Tree Regression on the Training set
    from sklearn.tree import DecisionTreeRegressor
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
    from sklearn.metrics import r2_score
    print(r2_score(y_test, y_pred))
    
def random_forest_regression(
    x_train,
    y_train,
    x_test,
    y_test,
    print_prediction=False,
):
    # DOESNT NEED FEATURE SCALING
    
    # Training the Random Forest Regression model on the Training set
    from sklearn.ensemble import RandomForestRegressor
    regressor = RandomForestRegressor(n_estimators=10,random_state=0)
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
    from sklearn.metrics import r2_score
    print(r2_score(y_test, y_pred))
