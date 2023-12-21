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
    """
    Base class for regression models.

    Parameters:
    - regressor_building_function (callable): A function that builds the regression model.
    - name (str): Name of the regression model (default is "Generic Regression Model").
    - default_parameters (dict): Default parameters for the regression model.

    Attributes:
    - regressor_building_function (callable): A function that builds the regression model.
    - name (str): Name of the regression model.
    - default_parameters (dict): Default parameters for the regression model.

    Methods:
    - train_the_model(x_train, y_train, **kwargs) -> LinearRegression|SVR|DecisionTreeRegressor|RandomForestRegressor:
      Train the regression model with the provided training data.

      Parameters:
      - x_train (np.ndarray): Input features for training.
      - y_train (np.ndarray): Target values for training.
      - **kwargs: Additional parameters for configuring the regression model.

      Returns:
      - LinearRegression|SVR|DecisionTreeRegressor|RandomForestRegressor: Trained regression model.

      Raises:
      - NotImplementedError: If the regressor building function is not defined.
    """
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
        """
        Train the regression model with the provided training data.

        Parameters:
        - x_train (np.ndarray): Input features for training.
        - y_train (np.ndarray): Target values for training.
        - **kwargs: Additional parameters for configuring the regression model.

        Returns:
        - LinearRegression|SVR|DecisionTreeRegressor|RandomForestRegressor: Trained regression model.

        Raises:
        - NotImplementedError: If the regressor building function is not defined.
        """
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
    """
    Child class representing the Multiple Linear Regression model.

    Parameters:
    - regressor_building_function (callable): A function that builds the regression model.
    - name (str): Name of the regression model (default is "Multiple Linear Regression").
    - default_parameters (dict): Default parameters for the regression model.

    Attributes:
    - regressor_building_function (callable): A function that builds the regression model.
    - name (str): Name of the regression model.
    - default_parameters (dict): Default parameters for the regression model.

    Methods:
    - multiple_linear_regression(x_train, y_train) -> LinearRegression:
      Train the Multiple Linear Regression model with the provided training data.

      Parameters:
      - x_train (np.ndarray): Input features for training.
      - y_train (np.ndarray): Target values for training.

      Returns:
      - LinearRegression: Trained Multiple Linear Regression model.

    - __init__(regressor_building_function=multiple_linear_regression, name="Multiple Linear Regression", default_parameters={}) -> None:
      Initialize the MultipleLinearRegression_ instance.

      Parameters:
      - regressor_building_function (callable): A function that builds the regression model.
      - name (str): Name of the regression model.
      - default_parameters (dict): Default parameters for the regression model.

      Returns:
      - None
    """ 
    @staticmethod
    def multiple_linear_regression(
        x_train: np.ndarray,
        y_train: np.ndarray,
    ) -> LinearRegression:  
        """
        Train the Multiple Linear Regression model with the provided training data.

        Parameters:
        - x_train (np.ndarray): Input features for training.
        - y_train (np.ndarray): Target values for training.

        Returns:
        - LinearRegression: Trained Multiple Linear Regression model.
        """
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
        """
        Initialize the MultipleLinearRegression_ instance.

        Parameters:
        - regressor_building_function (callable): A function that builds the regression model.
        - name (str): Name of the regression model.
        - default_parameters (dict): Default parameters for the regression model.

        Returns:
        - None
        """
        self.regressor_building_function = regressor_building_function
        self.name = name
        self.default_parameters = default_parameters
        return super().__init__()

class PolinomialRegression_ (RegressionModel):
    """
    Child class representing the Polynomial Regression model.

    Parameters:
    - regressor_building_function (callable): A function that builds the regression model.
    - name (str): Name of the regression model (default is "Polynomial Regression").
    - default_parameters (dict): Default parameters for the regression model.

    Attributes:
    - regressor_building_function (callable): A function that builds the regression model.
    - name (str): Name of the regression model.
    - default_parameters (dict): Default parameters for the regression model.

    Methods:
    - polynomial_regression(x_train, y_train, polynomial_degree=2) -> Pipeline:
      Train the Polynomial Regression model with the provided training data.

      Parameters:
      - x_train (np.ndarray): Input features for training.
      - y_train (np.ndarray): Target values for training.
      - polynomial_degree (int): Degree of the polynomial features.

      Returns:
      - Pipeline: Trained Polynomial Regression model.

    - __init__(regressor_building_function=polynomial_regression, name="Polynomial Regression", default_parameters={"polynomial_degree": 2}) -> None:
      Initialize the PolynomialRegression_ instance.

      Parameters:
      - regressor_building_function (callable): A function that builds the regression model.
      - name (str): Name of the regression model.
      - default_parameters (dict): Default parameters for the regression model.

      Returns:
      - None
    """ 
    @staticmethod
    def polinomial_regression(
        x_train: np.ndarray,
        y_train: np.ndarray,
        
        polynomial_degree:int = 2
    ) -> Pipeline:  
        """
        Train the Polynomial Regression model with the provided training data.

        Parameters:
        - x_train (np.ndarray): Input features for training.
        - y_train (np.ndarray): Target values for training.
        - polynomial_degree (int): Degree of the polynomial features.

        Returns:
        - Pipeline: Trained Polynomial Regression model.
        """
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
        """
        Initialize the PolynomialRegression_ instance.

        Parameters:
        - regressor_building_function (callable): A function that builds the regression model.
        - name (str): Name of the regression model.
        - default_parameters (dict): Default parameters for the regression model.

        Returns:
        - None
        """
        self.regressor_building_function = regressor_building_function
        self.name = name
        self.default_parameters = default_parameters
        return super().__init__()

class SupportVectorRegression_ (RegressionModel):
    """
    Child class representing the Support Vector Regression (SVR) model.

    Parameters:
    - regressor_building_function (callable): A function that builds the regression model.
    - name (str): Name of the regression model (default is "Support Vector Regression").
    - default_parameters (dict): Default parameters for the regression model.

    Attributes:
    - regressor_building_function (callable): A function that builds the regression model.
    - name (str): Name of the regression model.
    - default_parameters (dict): Default parameters for the regression model.

    Methods:
    - support_vector_regression(x_train, y_train, svr_kernel="rbf") -> SVR:
      Train the Support Vector Regression model with the provided training data.

      Parameters:
      - x_train (np.ndarray): Input features for training.
      - y_train (np.ndarray): Target values for training.
      - svr_kernel (str): Kernel type for SVR.

      Returns:
      - SVR: Trained Support Vector Regression model.

    - __init__(regressor_building_function=support_vector_regression, name="Support Vector Regression", default_parameters={"svr_kernel": "rbf"}) -> None:
      Initialize the SupportVectorRegression_ instance.

      Parameters:
      - regressor_building_function (callable): A function that builds the regression model.
      - name (str): Name of the regression model.
      - default_parameters (dict): Default parameters for the regression model.

      Returns:
      - None
    """ 
    @staticmethod
    def support_vector_regression(
        x_train: np.ndarray,
        y_train: np.ndarray,
        
        svr_kernel:str = "rbf"
    ):  
        """
        Train the Support Vector Regression model with the provided training data.

        Parameters:
        - x_train (np.ndarray): Input features for training.
        - y_train (np.ndarray): Target values for training.
        - svr_kernel (str): Kernel type for SVR.

        Returns:
        - SVR: Trained Support Vector Regression model.
        """
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
        """
        Initialize the SupportVectorRegression_ instance.

        Parameters:
        - regressor_building_function (callable): A function that builds the regression model.
        - name (str): Name of the regression model.
        - default_parameters (dict): Default parameters for the regression model.

        Returns:
        - None
        """
        self.regressor_building_function = regressor_building_function
        self.name = name
        self.default_parameters = default_parameters
        return super().__init__()
    
class DecisionTreeRegression_ (RegressionModel): 
    """
    Child class representing the Decision Tree Regression model.

    Parameters:
    - regressor_building_function (callable): A function that builds the regression model.
    - name (str): Name of the regression model (default is "Decision Tree Regression").
    - default_parameters (dict): Default parameters for the regression model.

    Attributes:
    - regressor_building_function (callable): A function that builds the regression model.
    - name (str): Name of the regression model.
    - default_parameters (dict): Default parameters for the regression model.

    Methods:
    - decision_tree_regression(x_train, y_train, random_state=0) -> DecisionTreeRegressor:
      Train the Decision Tree Regression model with the provided training data.

      Parameters:
      - x_train (np.ndarray): Input features for training.
      - y_train (np.ndarray): Target values for training.
      - random_state (int): Random seed for reproducibility.

      Returns:
      - DecisionTreeRegressor: Trained Decision Tree Regression model.

    - __init__(regressor_building_function=decision_tree_regression, name="Decision Tree Regression", default_parameters={"random_state": 0}) -> None:
      Initialize the DecisionTreeRegression_ instance.

      Parameters:
      - regressor_building_function (callable): A function that builds the regression model.
      - name (str): Name of the regression model.
      - default_parameters (dict): Default parameters for the regression model.

      Returns:
      - None
    """
    @staticmethod
    def decision_tree_regression(
        x_train: np.ndarray,
        y_train: np.ndarray,
        
        random_state:int = 0
    ):
        """
        Train the Decision Tree Regression model with the provided training data.

        Parameters:
        - x_train (np.ndarray): Input features for training.
        - y_train (np.ndarray): Target values for training.
        - random_state (int): Random seed for reproducibility.

        Returns:
        - DecisionTreeRegressor: Trained Decision Tree Regression model.
        """
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
        """
        Initialize the DecisionTreeRegression_ instance.

        Parameters:
        - regressor_building_function (callable): A function that builds the regression model.
        - name (str): Name of the regression model.
        - default_parameters (dict): Default parameters for the regression model.

        Returns:
        - None
        """
        self.regressor_building_function = regressor_building_function
        self.name = name
        self.default_parameters = default_parameters
        return super().__init__()

class RandomForestRegression_ (RegressionModel):
    """
    Child class representing the Random Forest Regression model.

    Parameters:
    - regressor_building_function (callable): A function that builds the regression model.
    - name (str): Name of the regression model (default is "Random Forest Regression").
    - default_parameters (dict): Default parameters for the regression model.

    Attributes:
    - regressor_building_function (callable): A function that builds the regression model.
    - name (str): Name of the regression model.
    - default_parameters (dict): Default parameters for the regression model.

    Methods:
    - random_forest_regression(x_train, y_train, number_of_estimators=50, random_state=0) -> RandomForestRegressor:
      Train the Random Forest Regression model with the provided training data.

      Parameters:
      - x_train (np.ndarray): Input features for training.
      - y_train (np.ndarray): Target values for training.
      - number_of_estimators (int): Number of trees in the forest.
      - random_state (int): Random seed for reproducibility.

      Returns:
      - RandomForestRegressor: Trained Random Forest Regression model.

    - __init__(regressor_building_function=random_forest_regression, name="Random Forest Regression", default_parameters={"number_of_estimators": 50, "random_state": 0}) -> None:
      Initialize the RandomForestRegression_ instance.

      Parameters:
      - regressor_building_function (callable): A function that builds the regression model.
      - name (str): Name of the regression model.
      - default_parameters (dict): Default parameters for the regression model.

      Returns:
      - None
    """
    @staticmethod 
    def random_forest_regression(
        x_train: np.ndarray,
        y_train: np.ndarray,
        
        number_of_estimators:int = 50,
        random_state:int = 0,
    ):  
        """
        Train the Random Forest Regression model with the provided training data.

        Parameters:
        - x_train (np.ndarray): Input features for training.
        - y_train (np.ndarray): Target values for training.
        - number_of_estimators (int): Number of trees in the forest.
        - random_state (int): Random seed for reproducibility.

        Returns:
        - RandomForestRegressor: Trained Random Forest Regression model.
        """
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
        """
        Initialize the RandomForestRegression_ instance.

        Parameters:
        - regressor_building_function (callable): A function that builds the regression model.
        - name (str): Name of the regression model.
        - default_parameters (dict): Default parameters for the regression model.

        Returns:
        - None
        """
        self.regressor_building_function = regressor_building_function
        self.name = name
        self.default_parameters = default_parameters
        return super().__init__()
