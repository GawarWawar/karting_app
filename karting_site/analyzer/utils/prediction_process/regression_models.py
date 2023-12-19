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
    def __init_subclass__(
        cls,
        regressor_building_function = None,
        name: str = "Generic Regression Model",
        default_parameters: dict = {},
    ) -> None:
        cls.regressor_building_function = regressor_building_function
        cls.name = name
        cls.default_parameters = default_parameters
        
    def train_the_model(
        self,
        x_train: np.ndarray,
        y_train: np.ndarray,

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
        x_train: np.ndarray,
        y_train: np.ndarray,
    ) -> LinearRegression:  
        # Training the Mulltiple Linear Regression model on the Training set
        regressor = LinearRegression()
        regressor.fit(
            x_train,
            y_train
        )

        return regressor
    
    def __init__(
        self,
        regressor_building_function: Callable[[np.ndarray,np.ndarray], LinearRegression] = multiple_linear_regression,
        name: str = "Multiple Linear Regression",
        default_parameters: dict = {},
    ) -> None:
        self.regressor_building_function = regressor_building_function
        self.name = name
        self.default_parameters = default_parameters
        return super().__init__()

class PolinomialRegression_ (RegressionModel): 
    @staticmethod
    def polinomial_regression(
        x_train: np.ndarray,
        y_train: np.ndarray,
        
        polynomial_degree:int = 2
    ) -> Pipeline:  
        # Create a pipeline that first applies polynomial features and then fits a linear regression model
        regressor = make_pipeline(
            PolynomialFeatures(polynomial_degree), LinearRegression()
        )

        # Fit the model to the training data
        regressor.fit(x_train, y_train)
        
        return regressor 
    
    def __init__(
        self,
        regressor_building_function: Callable[[np.ndarray,np.ndarray], Pipeline] = polinomial_regression,
        name: str = "Polinomial Regression",
        default_parameters: dict = {
            "polynomial_degree": 2
        }
    ) -> None:
        self.regressor_building_function = regressor_building_function
        self.name = name
        self.default_parameters = default_parameters
        return super().__init__()

class SupportVectorRegression_ (RegressionModel): 
    @staticmethod
    def support_vector_regression(
        x_train: np.ndarray,
        y_train: np.ndarray,
        
        svr_kernel:str = "rbf"
    ):  
        # Training the SVR model on the Training set
        regressor = SVR(
            kernel = svr_kernel,
        )
        
        regressor.fit(x_train, y_train)
        
        return regressor
    
    
    
    def __init__(
        self,
        regressor_building_function: Callable[[np.ndarray,np.ndarray], SVR] = support_vector_regression,
        name: str = "Support Vector Regression",
        default_parameters: dict = {
            "svr_kernel": "rbf"
        }
    ) -> None:
        self.regressor_building_function = regressor_building_function
        self.name = name
        self.default_parameters = default_parameters
        return super().__init__()
    
class DecisionTreeRegression_ (RegressionModel): 
    @staticmethod
    def decision_tree_regression(
        x_train: np.ndarray,
        y_train: np.ndarray,
        
        random_state:int = 0
    ):
        # Training the Decision Tree Regression on the Training set
        regressor = DecisionTreeRegressor(
            random_state = random_state
        )
        regressor.fit(x_train, y_train)

        return regressor
    
    def __init__(
        self,
        regressor_building_function: Callable[[np.ndarray,np.ndarray], DecisionTreeRegressor] = decision_tree_regression,
        name: str = "Decision Tree Regression",
        default_parameters: dict = {
            "random_state": 0
        }
    ) -> None:
        self.regressor_building_function = regressor_building_function
        self.name = name
        self.default_parameters = default_parameters
        return super().__init__()

class RandomForestRegression_ (RegressionModel):
    @staticmethod 
    def random_forest_regression(
        x_train: np.ndarray,
        y_train: np.ndarray,
        
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
    
    def __init__(
        self,
        regressor_building_function: Callable[[np.ndarray,np.ndarray], RandomForestRegressor] = random_forest_regression,
        name: str = "Random Forest Regression",
        default_parameters: dict = {
            "number_of_estimators": 50, 
            "random_state": 0,
        }
    ) -> None:
        self.regressor_building_function = regressor_building_function
        self.name = name
        self.default_parameters = default_parameters
        return super().__init__()
