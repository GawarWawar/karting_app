import numpy as np
import pandas as pd
import datetime

import time

def generate_new_id(
    main_df: pd.DataFrame(), # df to generate new id for
):
    '''
        Generates id based on the first column of the given DataFrame
    '''
    # We have place holder in each table, so we dont need to worry about 
        #nothing beeng in the table
    next_id = main_df.iloc[:,0].\
                iat[
                    len(main_df.index)-1
                ] + 1
    return(next_id)

def add_a_row (
    main_df: pd.DataFrame(), # df to add a row
    list_with_info: list() # List with a contant for the row
) -> None:
    '''
        Insert a new row into the end of the DataFrame with list_with_info content.
        Note: the length of list_with_info needs to be exact as amount of columns into the main_df.
    '''
    main_df.loc[len(main_df.index)]=list_with_info

def add_a_row_with_exact_time (
    main_df: pd.DataFrame(), # df to add a row
    list_with_info: list() # List with a contant for the row
) -> None:
    '''
        Insert a new row into the end of the DataFrame with list_with_info content and exact_time in the last column.
        Note: the length of list_with_info needs to be exact as amount of columns into the main_df - 1, because last column already contains exact_time.
    '''
    #getting system time for the exact moment
    exact_time = datetime.datetime.now()
    list_with_info.append(exact_time)
    add_a_row(main_df, list_with_info)

def add_a_row_with_id (
    main_df: pd.DataFrame(), # df to add a row
    list_with_info: list() # List with a contant for the row
) -> int:
    '''
        Insert a new row into the end of the Dataframe with id in the first column and list_with_info content.
        !Note: the length of list_with_info needs to be exact as amount of columns into the main_df - 1, because first column already contains id.
    '''
    row_content = [] # We need to create new list to get id in the 1st column
    next_id = generate_new_id(main_df)
    row_content.append(next_id)
    row_content.extend(list_with_info)
    add_a_row(main_df, row_content)
    return(next_id)
    
def add_a_row_with_id_and_exact_time (
    main_df: pd.DataFrame(), # df to add a row
    list_with_info: list() # List with a contant for the row
) -> int:
    '''
        Insert a new row into the end of the Dataframe with id in the first column, list_with_info content and exact_time in the last column.
        !Note: the length of list_with_info needs to be exact as amount of columns into the main_df - 2, because first column already contains id and last column already contains exact_time.
    '''
    row_content = [] # We need to create new list to get id in the 1st column
    next_id = generate_new_id(main_df)
    row_content.append(next_id)
    row_content.extend(list_with_info)
    add_a_row_with_exact_time(main_df, row_content)
    return(next_id)