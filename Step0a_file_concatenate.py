
import os
import re
import pandas as pd

def get_box_numbers(files_list):
    """
    :param files_list: list of the individual files within that directory (dtype:list)
    :return: box_num_list - box numbers from the individual files / dtype: list (parsed using regex)
    """
    box_num_list = []

    for full_path in files_list:
        file_name = full_path.split("/")[-1]  # File name is always the last in the list

        # Do NOT change the filename format (from Processing side) - Unless you want to change the regex below!
        # Regex
        box_num = re.findall(r'(?<=box)\d+', file_name)[0]  # Returns number following string "box" as a string
        box_num_list.append(box_num)

    return box_num_list


def return_multilevel_df_to_csv(files_list, box_numbers, col_names, selected_dir_title):
    """
    :param files_list: list of files to concatenate
    :param box_numbers: list of the actual box numbers extracted from files (instead of numbers by location)
    :param col_names: array of column names (usually ['event_code', 'timestamp', 'counter'])
    :param dir_title: path of the selected directory --> later to become title of csv file
    :return: saves multiindex dataframe into a csv within the Pycharm project folder --> change path later!
    """
    col_names = col_names
    files = files_list
    result = []

    for i in range(len(files)):
        f = files[i]
        df = pd.read_csv(f, sep=":", header=None, names=col_names)   # read_csv can also read in txt files! 
        result.append(df)

    multi_df = pd.concat(result, axis=1, keys=box_numbers, names=['Box Number', 'Columns'])
    df_title = os.path.basename(selected_dir_title)  # Returns the lowest directory of path (basename)

    return multi_df, df_title
