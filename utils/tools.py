import numpy as np
import pandas as pd
import json

def needed_rows(
    df_to_look_for_rows: pd.DataFrame,
    criteries: list
) -> pd.DataFrame:
    """ Finds multiple rows by given criterias

    Args:
        df_to_look_for_rows (pd.DataFrame): DataFrame in which we want to find rows\n
        criteries (list): List of Dictionaries with "column" and "criteria" combination:
            criteries = [{"column":"name_of_a_column", "criteria": criteria_value}]
            Note: programe will do criterias in order, so add them into criteries accordingly

    Returns:
        (list): Returns list of needed rows
    """
    for criteria in range(len(criteries)):
        df_to_look_for_rows = df_to_look_for_rows[
            df_to_look_for_rows.loc[:,criteries[criteria]["column"]] == \
                criteries[criteria]["criteria"]
        ].copy()
    return df_to_look_for_rows

def read_from_htmlfile(
    file_name
):
    # Importing BeautifulSoup class from the bs4 module
    from bs4 import BeautifulSoup

    # Opening the html file
    with open(file_name, "r") as HTMLFile:
        # Reading the file
        index = HTMLFile.read()
    
    # Creating a BeautifulSoup object and specifying the parser
    S = BeautifulSoup(index, 'lxml')

    body_content = str(S.body.contents[0])
    body_content = json.loads(body_content)

    return body_content

def create_body_content_file(
    body_content,
    file_path = "test_data/html.json"
):
    with open(file_path, "w") as JSONFile:
        json.dump(body_content, JSONFile, indent=2)
        
def write_log_to_file(
    logging_file_path,
    log_to_add
):
    with open(logging_file_path, "a") as logging_file:
        logging_file.write(log_to_add)

def create_file(
    path_to_file
):
    with open(path_to_file, "w") as file:
        pass
    
def str_lap_time_into_float_change(
    lap_time: str
):
    try:
        lap_time = float(lap_time)
    except ValueError:
        split_lap_time = lap_time.split(":")
        lap_time = float(split_lap_time[0])*60+float(split_lap_time[1])
    return lap_time