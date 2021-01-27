from natsort import natsorted, ns
import pandas as pd
from datetime import datetime

from Code_Dictionaries import *

## 0. Return Multiindex_Dataframe

def get_multi_df(file_path):
    multi_df = pd.read_csv(file_path, header=[0, 1], index_col=[0], low_memory=False)

    return multi_df

### 1. Return Multi Header Dictionary

def return_multi_header_dict(multi_df):
    '''
    :param multi_df: a multi-indexed data frame containing data from concatenated data spreadsheet.
    :return m_head_dict: dictionary with Key, Value pairs of Box #, Box Information Dictionary. 
                         Box Information Dictionary comprises Key, Value pairs of Label, Information. 
    '''

    m_head_dict = {}
    box_numbers = multi_df.columns.levels[0]  # Returns a "Frozen List"
    sorted_box_nums = natsorted(box_numbers)  # outputs a list of sorted box numbers

    for i in range(len(sorted_box_nums)):
        box_num = sorted_box_nums[i]
        ind_df = multi_df.loc[:, box_num]  # individual dataframe (box is type 'string')

        ind_df = ind_df.dropna(how='all')

        ## Header information from Processing side! (thus, incorrect input into Processing will return incorrect output)
        start_code_idx = ind_df.index[ind_df.event_code.isin(['0113','113'])].tolist()[0]  # the list will only contain ONE element
        end_date_info = ind_df[-2:]  # last two rows will always be end date info

        head = ind_df[:start_code_idx]

        ind_head = pd.concat([head, end_date_info], axis=0)
        # header dictionary requires end date/time info so need to concatenate the top and bottom dfs

        ind_head['timestamp'] = ind_head['timestamp'].str.strip()

        # # {first column: second column}
        ind_header_dict = {row[0]: row[1] for row in ind_head.values}  # .values --> transforms into numpy array

        m_head_dict[box_num] = ind_header_dict

    return m_head_dict


### 2. Return Multi Body Dataframe

def return_multi_body_df(multi_df, columns):
    '''
    :param multi_df: a multi-indexed data frame containing data from concatenated data spreadsheet. 
                    1st level: Box #, 2nd level: [event_code, timestamp, counter] 
    :param columns: New column names for output dataframe. Typically hardcoded in main run-script.
    :return m_body_df: An updated version of multi_df that now includes a level containing the event_string
                       label for the event codes: [event_string, event_cod, timestamp, counter]
    '''


    result = []; box_arr = []
    box_numbers = multi_df.columns.levels[0]
    sorted_box_nums = natsorted(box_numbers) # outputs a list of sorted box numbers

    for i in range(len(sorted_box_nums)):  # for all the boxes, (outermost index is box number)
        box_num = sorted_box_nums[i]
        ind_df = multi_df.loc[:, box_num]  # individual dataframe

        ind_df = ind_df.dropna(how='all')
        # ind_df['event_code'] = ind_df['event_code'].astype('str')  # Changed

        # Extracting ACTUAL BODY
        header_end_idx = ind_df.loc[ind_df[ind_df.columns[0]] == '9070'].index[0]  # after IRs get initialized correctly
        body_start_idx = header_end_idx + 1

        body = ind_df[body_start_idx:-2].reset_index(drop=True)
        body.loc[:,'timestamp'] = pd.to_numeric(body['timestamp'])  # change to numeric dtype
        body['event_string'] = body['event_code'].map(event_code_dict)

        body = body[columns]  # 4 columns or 3 columns

        box_arr.append(box_num)
        result.append(body)

    m_body_df = pd.concat(result, axis=1, keys=box_arr, names=['Box Number', 'Columns'])

    return m_body_df


### 3. Get Start End Time

def get_start_end_time(m_head_dict):
    '''
    :param m_head_dict: multi-dictionary returned by return_multi_header_dict. 
    :return start_end_time_dict: a dictionary with key, value pairs of box#, tuple containing
                                 start and end times (in that order) as datetime objects. 
    '''
    start_end_time_dict = {}
    for box_num in m_head_dict.keys():
        # Start Datetime
        start_datetime = f'{m_head_dict[box_num]["Start Date"]} {m_head_dict[box_num]["Start Time"]}'.replace('-', ':')
        start_time = datetime.strptime(start_datetime, '%m/%d/%Y %H:%M:%S')
        # End Datetime
        end_datetime = f'{m_head_dict[box_num]["End Date"]} {m_head_dict[box_num]["End Time"]}'.replace('-', ':')
        end_time = datetime.strptime(end_datetime, '%m/%d/%Y %H:%M:%S')

        start_end_time_dict[box_num] = (start_time, end_time)
    return start_end_time_dict



### 4. Return Multi Datetime Dataframe

def return_multi_dt_df(m_head_dict, m_body_df, start_end_time_dict):
    '''
    :param m_head_dict: dictionary output of return_multi_header_dict.
    :param m_body_df: DataFrame output of return_multi_body_df
    :param start_end_time_dict: dictionary output of get_start_end_time
    :return m_dt_df: an expanded version of m_body_df with the following levels
                    at each level of Box#: [event_string, event_cod, timestamp, counter, datetime_realtime, day, hour]
    '''
    result = []; box_arr = list(m_body_df.columns.levels[0])
    midx_shape = m_body_df.columns.levshape   # (returns a tuple)

    # # # Exception Handling
    if (len(m_head_dict) != midx_shape[0]):   # This indicates the number of boxes
        raise ValueError('Number of boxes in dictionary and dataframe does not match')

    for i in range(len(box_arr)):  # for all the boxes in box_array
        box_num = box_arr[i]
        ind_df = m_body_df.loc[:, box_num]  # individual dataframe / box_num --> class 'string'

        ind_df = ind_df.dropna(how='all')

        start_time = start_end_time_dict[box_num][0]
        # end_time = start_end_time_dict[box_num][1]

        # # Broadcast new columns
        ind_df['datetime_realtime'] = start_time + pd.to_timedelta(pd.to_numeric(ind_df['timestamp']), unit='ms')
        ind_df['day'] = ind_df['datetime_realtime'].dt.day
        ind_df['hour'] = ind_df['datetime_realtime'].dt.hour  # using the .dt accessor to access datetime object

        # box_arr.append(box_num)
        result.append(ind_df)

    m_dt_df = pd.concat(result, axis=1, keys=box_arr, names=['Box Number', 'Columns'])

    return m_dt_df



### 5. Fill Counter Datetime Column --> fill in datetime for counter value columns

def fill_counter_datetime_col(m_dt_df):
    '''
    :param m_dt_df: multi-index dataframe returned by return_multi_dt_df.
    :return m_dt_df_imputed: An almost identical dataframe with timestamps now included
                             for counter variables in datetime_filled. In m_dt_df only 
                             non-counter variables had timestamps. 
    '''
    result = []; box_arr = list(m_dt_df.columns.levels[0])
    # midx_shape = m_dt_df.columns.levshape   # (returns a tuple)

    for i in range(len(box_arr)):  # for all the boxes in box_array
        box_num = box_arr[i]
        ind_df = m_dt_df.loc[:, box_num]  # individual dataframe / box_num --> class 'string'

        ind_df = ind_df.dropna(how='all')

        first_row_timestamp = ind_df.iloc[0]['timestamp']
        last_row_timestamp = ind_df.iloc[-1]['timestamp']

        ind_df_impute = ind_df.copy()

        # # Two if statements to ensure columns get filled in every case
        # # Even if BOTH first row and last row are NaN values

        if pd.isnull(first_row_timestamp):
            ind_df_impute['datetime_filled'] = ind_df_impute.datetime_realtime.fillna(method='bfill')

        # # Column updating!
        if pd.isnull(last_row_timestamp):
            ind_df_impute['datetime_filled'] = ind_df_impute['datetime_filled'].fillna(method='ffill')

        # # If none of the first/last rows are none, just use bfill method
        else:
            ind_df_impute['datetime_filled'] = ind_df_impute.datetime_realtime.fillna(method='bfill')

        result.append(ind_df_impute)

    # box_arr from above (before the for loop)
    m_dt_df_imputed = pd.concat(result, axis=1, keys=box_arr, names=['Box Number', 'Columns'])

    return m_dt_df_imputed



### 6. Return Multi Parsed Datetime Dataframe

def return_multi_parsed_dt_df(m_dt_df_imputed, start_parsetime, end_parsetime):
    '''
    :param m_dt_df_imputed: multi-index dataframe returned by fill_counter_datetime_col.
    :param start_parsetime: Time and date from which to start slicing (string format, 'YYYY/mm/dd HH:MM')
    :param end_parsetime: Time and date at which to stop slicing (same format).
    :return m_parsed_dt_df: a slice of m_dt_df_imputed containing data from all boxes
                            between start_parsetime and end_parsetime. 
    '''


    # # Parse Time Criteria for all files (boxes)
    start_dt = datetime.strptime(start_parsetime, '%Y/%m/%d %H:%M')
    end_dt = datetime.strptime(end_parsetime, '%Y/%m/%d %H:%M')

    # # Boilerplate for Multilevel Dataframe
    result = []; box_arr = list(m_dt_df_imputed.columns.levels[0])

    for i in range(len(box_arr)):
        box_num = box_arr[i]
        ind_df = m_dt_df_imputed.loc[:, box_num]  # individual dataframe
        # No need for conversion to str(box_num) since box_num is already string

        ind_df = ind_df.dropna(how='all')

        # 1. Parse by time
        # # : Problem --> counter values don't have timestamps, thus need to index the dataframe
        # # : Problem solved by imputing datetimes
        p_body = ind_df[(ind_df['datetime_filled'] >= start_dt) & (ind_df['datetime_filled'] <= end_dt)]

        result.append(p_body)

    m_parsed_dt_df = pd.concat(result, axis=1, keys=box_arr, names=['Box Number', 'Columns'])

    return m_parsed_dt_df



### 7. Wrapper Function (Final Multi Header and Parsed Datetime Dataframe)

def final_m_header_and_parsed_dt_df(multi_df, columns, start_parsetime, end_parsetime):

    # # Reading in multilevel dataframe
    # multi_df = pd.read_csv(file, header=[0,1], index_col=[0], low_memory=False)

    m_head_dict = return_multi_header_dict(multi_df)
    m_body_df = return_multi_body_df(multi_df, columns)

    # # Dictionary of start/end time tuples
    m_start_end_time_dict = get_start_end_time(m_head_dict)

    # # Returns dataframe with imputed datetime
    m_dt_df = return_multi_dt_df(m_head_dict, m_body_df, m_start_end_time_dict)
    m_dt_df_imputed = fill_counter_datetime_col(m_dt_df)

    m_parsed_dt_df = return_multi_parsed_dt_df(m_dt_df_imputed, start_parsetime, end_parsetime)

    return m_head_dict, m_parsed_dt_df




