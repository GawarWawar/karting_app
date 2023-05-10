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
        (list): Returns list of needed indexes
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
    body_content
):
    with open("html.json", "w") as JSONFile:
        json.dump(body_content, JSONFile, indent=2)