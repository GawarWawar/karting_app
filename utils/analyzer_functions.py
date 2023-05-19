import pandas as pd
import numpy as np
import requests

import time

import sys
from os.path import dirname, abspath
import importlib.util

#SCRIPT_DIR = dirname(abspath(__file__))
#path = sys.path.append(dirname(SCRIPT_DIR))

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

def records_columns_to_numeric (
    df_of_records: pd.DataFrame,
    columns_to_change: list
):
    for column in columns_to_change:
        try:
            df_of_records[column]=pd.to_numeric(df_of_records[column])
        except ValueError:
            for i in range(len(df_of_records.loc[:, column])):
                df_of_records.loc[i, column] = u_tools.str_lap_time_into_float_change(df_of_records.loc[i, column])
            df_of_records[column]=pd.to_numeric(df_of_records[column])
    
    return df_of_records

def module_to_create_df_with_statistic(
    df_of_records: pd.DataFrame, 
    
    df_of_thing: pd.DataFrame,
    column_to_look_for_thing: str,
    
    column_name_to_look_for_values_in: str,
    
    column_name_to_put_mean_value_in: str = None,
    column_name_to_put_min_value_in: str = None,
):
    for thing in df_of_thing.loc[:, column_to_look_for_thing]:
        all_thing_records = df_of_records.loc[
                df_of_records.loc[:, column_to_look_for_thing] == thing,
                :
        ]
        
        if column_name_to_put_mean_value_in != None:
            df_of_thing.loc[
                df_of_thing.loc[:, column_to_look_for_thing] == thing,
                column_name_to_put_mean_value_in
            ] = all_thing_records.loc[:, column_name_to_look_for_values_in].mean()
        
        if column_name_to_put_min_value_in != None:
            df_of_thing.loc[
                df_of_thing.loc[:, column_to_look_for_thing] == thing,
                column_name_to_put_min_value_in
            ] = all_thing_records.loc[:, column_name_to_look_for_values_in].min()
        
    return df_of_thing
        
        

def module_to_create_pilot_statistics (
    df_of_records: pd.DataFrame,
):
    df_of_pilots = df_of_records.loc[
        (df_of_records.loc[:, "true_name" ]== True), 
        "pilot"
    ].drop_duplicates().copy().T.to_frame()
    df_of_pilots = df_of_pilots.reset_index(drop=True)
    
    df_of_pilots["pilot_temp"] = 0
    df_of_pilots["pilot_fastest_lap"] = 0
    
    module_to_create_df_with_statistic(
        df_of_records=df_of_records,
        
        df_of_thing=df_of_pilots,
        column_to_look_for_thing="pilot",
        
        column_name_to_put_mean_value_in="pilot_temp",
        column_name_to_put_min_value_in="pilot_fastest_lap",
        column_name_to_look_for_values_in="lap_time",
    )
        
    return df_of_pilots

def module_to_create_kart_statistics (
    df_of_records: pd.DataFrame,
    category: str
):
    df_of_karts = df_of_records.loc[
        df_of_records.loc[:, "true_kart" ]== True,
        category
    ].drop_duplicates().T.to_frame()
    
    df_of_karts["kart_fastest_lap"] = 0
    
    module_to_create_df_with_statistic(
        df_of_records=df_of_records,
        
        df_of_thing=df_of_karts,
        column_to_look_for_thing=category,
        
        #column_name_to_put_mean_value_in="kart_temp",
        column_name_to_put_min_value_in="kart_fastest_lap",
        column_name_to_look_for_values_in="lap_time",
    )
    
    return df_of_karts
 
def regression_process(
      df_to_analyze: pd.DataFrame,  
):
    x = df_to_analyze.iloc[:, :-1].values # Matrix of Features
    y = df_to_analyze.iloc[:, -1].values # Depending variable vector
    
    # Encoding the Independent Variable
    from sklearn.compose import ColumnTransformer
    from sklearn.preprocessing  import OneHotEncoder
    
    ohe = OneHotEncoder()
    ct = ColumnTransformer(
        transformers=[("encoder", ohe, [0,1])],
        remainder="passthrough"
    )
    x = ct.fit_transform(x).toarray()
    
    # Splitting the dataset into the Training set and Test set
    from sklearn.model_selection import train_test_split
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
    
    regres_eval.random_forest_regression(
        x_train,
        y_train,
        x_test,
        y_test,
        print_prediction
    )
    