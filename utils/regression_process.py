import pandas as pd
import numpy as np
import requests

import time

import sys
from os.path import dirname, abspath
import importlib.util

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing  import OneHotEncoder
from sklearn.model_selection import train_test_split

from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor


if __name__ == "__main__":
    import add_row
    import tools as u_tools
    import regression_evaluation as regres_eval
else:
    spec = importlib.util.spec_from_file_location("add_row", "utils/add_row.py")
    add_row = importlib.util.module_from_spec(spec)
    sys.modules["add_row"] = add_row
    spec.loader.exec_module(add_row)

    spec = importlib.util.spec_from_file_location("u_tools", "utils/tools.py")
    u_tools = importlib.util.module_from_spec(spec)
    sys.modules["u_tools"] = u_tools
    spec.loader.exec_module(u_tools)
    
    spec = importlib.util.spec_from_file_location("regres_eval", "utils/regression_evaluation.py")
    regres_eval = importlib.util.module_from_spec(spec)
    sys.modules["regres_eval"] = regres_eval
    spec.loader.exec_module(regres_eval)


def regression_process(
      df_to_analyze: pd.DataFrame,  
):
    x = df_to_analyze.iloc[:, :-1].values # Matrix of Features
    y = df_to_analyze.iloc[:, -1].values # Depending variable vector
    
    # Encoding the Independent Variable
    ct = ColumnTransformer(
        transformers=[("encoder", OneHotEncoder(), [0,1])],
        remainder="passthrough"
    )
    x = ct.fit_transform(x).toarray()
    
    # Splitting the dataset into the Training set and Test set
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2, random_state = 0)
    
    print_prediction = False
    
    regres_eval.multiple_linear_regression(
        x_train,
        y_train,
        x_test,
        y_test,
        print_prediction
    )
    
    regres_eval.polinomial_regression(
        x_train,
        y_train,
        x_test,
        y_test,
        print_prediction
    )
    
    regres_eval.support_vector_regression(
        x_train,
        y_train,
        x_test,
        y_test,
        print_prediction
    )
    
    regres_eval.decision_tree_regression(
        x_train,
        y_train,
        x_test,
        y_test,
        print_prediction
    )
    
    regressor = regres_eval.random_forest_regression(
        x_train,
        y_train,
        x_test,
        y_test,
        print_prediction
    )