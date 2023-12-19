import numpy as np
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline, Pipeline

from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor

from sklearn.metrics import r2_score
from sklearn.utils.validation import column_or_1d 

from collections.abc import Callable

class RegressionModel ():
    regressor_building_function = None
    name = "Generic Regression Model"
    default_parameters = {}
        
    def train_the_model(
        self,
        x_train: list,
        y_train: list,

        **kwargs
    ) -> LinearRegression|SVR|DecisionTreeRegressor|RandomForestRegressor:
        if self.regressor_building_function is None:
            raise NotImplementedError("Regressor building function is not defined.")
        
        additional_parameters = {**self.default_parameters, **kwargs}
        regressor = self.regressor_building_function(
            x_train,
            y_train,
            **additional_parameters
        )
    
        return regressor
        
class MultipleLinearRegression_ (RegressionModel): 
    @staticmethod
    def multiple_linear_regression(
        x_train: list,
        y_train: list,
    ) -> LinearRegression:  
        # Training the Mulltiple Linear Regression model on the Training set
        regressor = LinearRegression()
        regressor.fit(
            x_train,
            y_train
        )

        return regressor
    
    regressor_building_function = multiple_linear_regression
    name = "Multiple Linear Regression"

class PolinomialRegression_ (RegressionModel): 
    @staticmethod
    def polinomial_regression(
        x_train: list,
        y_train: list,
        
        polynomial_degree:int = 2
    ) -> Pipeline:  
        # Create a pipeline that first applies polynomial features and then fits a linear regression model
        regressor = make_pipeline(
            PolynomialFeatures(polynomial_degree), LinearRegression()
        )

        # Fit the model to the training data
        regressor.fit(x_train, y_train)
        
        return regressor 
    
    regressor_building_function = polinomial_regression
    name = "Polinomial Regression"
    default_parameters = {
        "polynomial_degree": 2
    }

class SupportVectorRegression_ (RegressionModel): 
    @staticmethod
    def support_vector_regression(
        x_train: list,
        y_train: list,
        
        svr_kernel:str = "rbf"
    ):  
        # Training the SVR model on the Training set
        regressor = SVR(
            kernel = svr_kernel,
        )
        
        regressor.fit(x_train, y_train)
        
        return regressor
    
    regressor_building_function = support_vector_regression
    name = "Support Vector Regression"
    default_parameters = {
        "svr_kernel": "rbf"
    }
    
class DecisionTreeRegression_ (RegressionModel): 
    @staticmethod
    def decision_tree_regression(
        x_train,
        y_train,
        
        random_state:int = 0
    ):
        # Training the Decision Tree Regression on the Training set
        regressor = DecisionTreeRegressor(
            random_state = random_state
        )
        regressor.fit(x_train, y_train)

        return regressor
    
    regressor_building_function = decision_tree_regression
    name = "Decision Tree Regression"
    default_parameters = {
        "random_state": 0
    }

class RandomForestRegression_ (RegressionModel):
    @staticmethod 
    def random_forest_regression(
        x_train,
        y_train,
        
        number_of_estimators:int = 50,
        random_state:int = 0,
    ):  
        # Training the Random Forest Regression model on the Training set
        regressor = RandomForestRegressor(
            n_estimators=number_of_estimators,
            random_state=random_state,
        )
        regressor.fit(x_train, y_train)
        
        return regressor

    regressor_building_function = random_forest_regression
    name = "Random Forest Regression"
    default_parameters = {
        "number_of_estimators": 50,
        "random_state": 0,
    }
