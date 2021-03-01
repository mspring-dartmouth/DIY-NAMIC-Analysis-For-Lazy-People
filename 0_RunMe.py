#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Created on Thu Jun 25 15:07:10 2020

@author: Ichimaru
'''


#from Step_0_Settings import *    # import everything
from Step0a_file_concatenate import *
from Step1a_timeframe_parsing import *
from Step1c_paradigm_metrics import *
from Step2a_combine_and_categorize_by_metrics import *
from Step8b_latency import *
from Tkinter_Selection_Ka_Modified import select_all_files_in_directory
from Tkinter_Selection_Ka_Modified import select_and_sort_directory_contents
from Tkinter_Selection_Ka_Modified import select_single_dir
from Tkinter_Selection_Ka_Modified import select_single_file

from collections import defaultdict
from collections import Counter

import os  # for moving files
import shutil # for moving files 
import sys
import time
import numpy
import datetime
from datetime import timedelta
import pandas as pd
import time 
import re # for spliting strings with multlple delimers 
from natsort import natsorted


###################################
#         Get user input          #
###################################

# Bin needs to be in hours.  To do minutes,  change line 245
print('Files with acquisition time less than the user defined analysis bin size will <<NOT>> be analyzed even though the files will still be sorted')
Bin = input ('What is the analysis bin size in hours? \n(Integer input, lab default is "23")\n\n')
ExtraBin = input('There are residual time leftover in the end of the files.  Select a bin size threshold (in hours) to export those leftover time or type in the same bin size again if you don"t want those residual times. \n(Integer/Float input, lab default is "15") \n\n ')
YesToLatency = input ('\n We will export the count data.\n However, latency data with small analysis time window (e.g. 2 hrs) can cause errors.\n Do you also want to export latency data? (y/n).) )\n\n')


# # Directory Selection
try: # If user provided pathname to data, use it.
    file_pattern = os.path.join(sys.argv[1], '*.txt')
    files_list = natsorted(glob.glob(file_pattern), alg=ns.IGNORECASE)
    selected_dir_title = os.path.basename(sys.argv[1])

except IndexError: # If no argument provided, prompt for selection.
    print('\n\n Where is your data? (Please select Path from opened window) ')    
    (files_list, selected_dir_title) = select_all_files_in_directory()

box_numbers = get_box_numbers(files_list)
file_count = len(files_list)
time.sleep(2) # add some delay time

print(f'\n Thank you,  I found {file_count} text file(s)')

time.sleep(2) # add some delay time

if len(files_list) == 0:
    print('\n Please try again.  We are looking for data files in ".txt" format ')
    time.sleep(5)
    sys.exit() # kill program 
    
    
time.sleep(2) # add some delay time

try: # If user provided second argument, use it as output path. 
    file_path = sys.argv[2]
except IndexError:  # If not, prompt for input.
    print('\n Where should we save the analysis files? (Please select Path)')
    ## Pick the file path! (single file (output from Step 0)
    file_path = select_single_dir()
    time.sleep(2) # add some delay time
    print('\n Thank you!')


#####################################
#Set up directories for output files#
#####################################


OUTDIR = os.path.join(file_path, 'DIY-NAMIC_Analysis_Output')  # Put data files into folders

if os.path.isdir(OUTDIR): #  remove previous ananlysis folder if in the same location
    print('\n I detected analysis folder from previous run. The folder "DIY-NAMIC_Analysis_Output" will be replaced.  ')
    shutil.rmtree(OUTDIR)


if not os.path.isdir(OUTDIR):  #  only create output folder if output link does not already exist
    os.mkdir(OUTDIR)
    
    IOUTDIR_Rearranged_Data = os.path.join(OUTDIR, 'Rearranged_Data')  # Path for creating individual particpant output folder for saving data
    if not os.path.isdir(IOUTDIR_Rearranged_Data):  # only creat output folder if output link  does not exist 
        os.mkdir(IOUTDIR_Rearranged_Data)
    
    IOUTDIR_Analysis_Output = os.path.join(OUTDIR, 'Analysis_Output')  # Path for creating individual particpant output folder for saving data
    if not os.path.isdir(IOUTDIR_Analysis_Output):  # only creat output folder if output link  does not exist 
        os.mkdir(IOUTDIR_Analysis_Output)
file_name =[]
for i in range(file_count):
    full_path = files_list[i]
    #file_name.append(full_path.split("/")[-1])  # File name is always the last in the list
    #file_name.append(full_path.split("\\")[-1])  # File name is always the last in the list # Modified for Windows Computer
    file_name.append(re.split(r'/|\\', full_path)[-1])

print(f'\n\n Your Analysis Output will be located in {OUTDIR}')
print('\n Please wait while we export the data')
start = time.time()  #  for calculating runtime 



varnames = []
stop_script = 0
varnames.extend(['Start Date', 'Start Time', 'Mouse Line', 'Experiment', 'Paradigm', 'Group', 'Sex', 'Subject', 'Box Number', '0113']) # dictionary for file info
varnames.extend(['7070', '8070','9070','5521']) # inintal timestamps
varnames.extend(['End Date', 'End Time'])


#create dictionary 

file_info = defaultdict(list)
for xx in range(file_count):  # go through each file 

    temp_file_info = {}
    col_names = ['event_code', 'timestamp', 'counter'] # For TIR (Groups 1,2)
    df = pd.read_csv(files_list[xx], sep=":", header=None, names=col_names)
      
    # Make sure each of the expected variables is present at least once in each file.
    # Loop through variables and find first instance in each file. 
    for var_name in varnames:    
        error = 1 
        if var_name in df.loc[:, 'event_code'].values:
            # If the variable is present, store index of its first appearance...
            first_index = df[df.event_code==var_name].index[0]
            temp_file_info[var_name] = df.loc[first_index, 'timestamp'] 
            # and reset error to False.
            error = 0
        # If the variable is not present, alert user and store stop-state. 
        if (error == 1 ):
            stop_script = 1
            print(f'\n There is missing information in "{var_name}" for text file \n "{file_name[xx]}" ')
            temp_file_info[var_name]= 'NaN'  #  Space holder for when data is missing 
            
    
    #append individual file information to overall file information
    for j in varnames:
        file_info[j].append(temp_file_info[j])


if (stop_script == 1):
    print('\n Sorry, we have to stop the analysis.  There is missing information in the data file(s).  You need to fix the above file(s) before proceeding. ')
    sys.exit()  # exit the program
    
    
    
#  Create new folders to organize data 
temp_file_list = []

for j in range(file_count):
    temp_file_list.append(file_info['Paradigm'][j]+ '-_-'+ file_info['Start Date'][j])

# I can't for the life of me figure out what the purpose of Counter is here. 
# It SEEMS like it's basically just acting as set(), but I'm not sure. 
temp_item_list = list(Counter(temp_file_list).keys())
# Create an intermediate iterable in which all the spaces are removed.
no_space_temp_item_list = map(lambda x: x.replace(' ', ''), temp_item_list)
# Finalize names by replacing '/' with '_'. Store as list.
final_item_list = list(map(lambda x: x.replace('/', '_'), no_space_temp_item_list))
# final_item_list contains a list of unique paradigms found in the datafiles, 
# which may only be a single element.

for f_name in final_item_list:
    
    IOUTDIR_temp = os.path.join(IOUTDIR_Rearranged_Data, f_name)  # Path for creating individual participant output folder for saving data
    if not os.path.isdir(IOUTDIR_temp):  # only create output folder if output link  does not exist 
        os.mkdir(IOUTDIR_temp)

#  Copy files to new rearrange folder 
for j in range(file_count):
    IOUTDIR_temp = os.path.join(IOUTDIR_Rearranged_Data, (temp_file_list[j].replace(' ', '')).replace('/', '_')+'/'+file_name[j])
    shutil.copyfile(files_list[j],IOUTDIR_temp )
    

###################################
#   Step_0a_file_concatenate.py   #
###################################
#Concatenate raw files into a single output spreadsheet. 


# Begin by creating necessary directories. 
IOUTDIR_Concat_files = os.path.join(IOUTDIR_Analysis_Output, 'Concat_files')  # Path for creating individual participant output folder for saving data
if not os.path.isdir(IOUTDIR_Concat_files):  # only create output folder if output link  does not exist 
    os.mkdir(IOUTDIR_Concat_files)

# Then iterate over paragdigms and create a single df containing information from all files containing data from that paradigm.
for f_name in final_item_list:
    IOUTDIR_temp = os.path.join(IOUTDIR_Rearranged_Data, f_name)
    
    # # Directory Selection
    (files_list, selected_dir_title) = select_and_sort_directory_contents(IOUTDIR_temp)
    box_numbers = get_box_numbers(files_list)

    # # returns multi_df and its future title
    (df, title) = return_multilevel_df_to_csv(files_list, box_numbers, col_names, selected_dir_title)

    # # Saves the dataframe at THIS stage (otherwise Pycharm crashes if I try to save it without returning the df first!)
    df.to_csv(os.path.join(IOUTDIR_Concat_files, "{}_concat.csv".format(title)))


###################################
#        Latency Analysis         #
###################################

# Create output directories to store individual participant files AND 
# store file paths as variables for use in later code. 

IOUTDIR_M_files = os.path.join(IOUTDIR_Analysis_Output, 'M_files')  
IOUTDIR_Latency_Response = os.path.join(IOUTDIR_Analysis_Output, 'Latency_Response')  
IOUTDIR_Latency_Retrieval = os.path.join(IOUTDIR_Analysis_Output, 'Latency_Retrieval')  
IOUTDIR_Latency_Initiation = os.path.join(IOUTDIR_Analysis_Output, 'Latency_Initiation')  

for directory in [IOUTDIR_M_files, IOUTDIR_Latency_Response, IOUTDIR_Latency_Retrieval, IOUTDIR_Latency_Initiation]:
    if not os.path.isdir(directory): 
        os.mkdir(directory)

processed_list = []
processed_p_list = []
processed_date_list = []

# Iterate over concat files by iterating over info strings in final_item_list.
# info string format: PARADIGMNAME-_-MM_DD_YYYY
for run_info_string in final_item_list:
    
    # Pull out paradigm name and date from run_info_string
    TempParadigm = run_info_string.split("-_-")[0]
    TempDate =  (run_info_string.split("-_-")[1]).replace('_', '/')
    
     # grab individual csv header info for each concat file
    TempStartDate = []
    TempStartTime = []
    TempEndDate = []
    TempEndTime = []
    

    for i in range(file_count):
        # Check the date and paradigm for each file against the date and paradigm for the current loop.
        if(((file_info['Start Date'][i]).replace(' ', '') == TempDate) & ((file_info['Paradigm'][i]).replace(' ', '') == TempParadigm)):
            
            # If they match, store the start and end times from the file.
            TempStartDate.append((file_info['Start Date'][i]).replace(' ', ''))
            TempStartTime .append((file_info['Start Time'][i]).replace(' ', ''))
            TempEndDate.append((file_info['End Date'][i]).replace(' ', ''))
            TempEndTime.append((file_info['End Time'][i]).replace(' ', ''))
            
            
            
            
            
    #find the latest start time and earliest end time 
  
    datetimeFormat = '%Y/%m/%d %H:%M'

    # Pull first start date and reformat to match datetimeFormat
    ref_date_as_datetime = datetime.datetime.strptime(TempStartDate[0], '%m/%d/%Y')
    ReferenceTime = '{} 00:00'.format(datetime.datetime.strftime(ref_date_as_datetime, '%Y/%m/%d'))
    ref_time_as_datetime = datetime.datetime.strptime(ReferenceTime, datetimeFormat)

    # Determine the time between reference and the start time of each file.
    TempDurationSeconds = []
    # Initiate a storage variable to keep track of max value. Negative initial value is guaranteed to be lower. 
    max_time = -1 
    for k in range(len(TempStartDate)):
        # Create datetime object from date and time of current iteration.
        curr_date_as_datetime = datetime.datetime.strptime(TempStartDate[k], '%m/%d/%Y')
        curr_time_as_datetime = datetime.datetime.strptime(TempStartTime[k], '%H-%M-%S').time()
        TestTime = datetime.datetime.combine(curr_date_as_datetime, curr_time_as_datetime)
        
        # Do the math and convert to seconds. 
        diff = TestTime - ref_time_as_datetime
        TimeinSeconds = diff.days * 24 * 3600 + diff.seconds

        # Check if it's the max and store it as a possible start time if it is.
        if TimeinSeconds > max_time:
            max_time = TimeinSeconds
            PossibleStartTime = datetime.datetime.strftime(TestTime, datetimeFormat)

    # Min time is tracked using a different method. See loop.
    for l in range(len(TempEndDate)):
        curr_date_as_datetime = datetime.datetime.strptime(TempEndDate[l], '%m/%d/%Y')
        curr_time_as_datetime = datetime.datetime.strptime(TempEndTime[l], '%H-%M-%S').time()
        TestTime = datetime.datetime.combine(curr_date_as_datetime, curr_time_as_datetime)
        diff = TestTime - ref_time_as_datetime
        TimeinSeconds = diff.days * 24 * 3600 + diff.seconds

        # Next check if it's the minimum value:
        try:
            if TimeinSeconds < min_time:
                curr_time_is_min = True
            else:
                curr_time_is_min = False
        except NameError:
            # If min_time does not exist, it's the first loop. Store current time as min_time. 
            # NB: min_time cannot be instantiated with an arbitrary value because it cannot be
            # guaranteed to be greater than all possible values of TimeinSeconds. 
            curr_time_is_min = True

        if curr_time_is_min:
            min_time = TimeinSeconds
            PossibleEndTime = datetime.datetime.strftime(TestTime, datetimeFormat)


 
    # Export data in bin (23 hour blocks), last block is whatever time left until Possible End time. 
    diff = datetime.datetime.strptime(PossibleEndTime, datetimeFormat)- datetime.datetime.strptime(PossibleStartTime, datetimeFormat)
    TimeinSeconds = diff.days *24 * 3600 + diff.seconds
    NumOfHours = TimeinSeconds /3600
    Suggested_Number_of_Run = int(NumOfHours/float(Bin))
    
    
    Timelist = []
    Timelist.append(PossibleStartTime)
    NextTimeStamp = PossibleStartTime
    
    for m in range(Suggested_Number_of_Run):  # subtract one for the begining timestamp 
        NextTimeStamp = datetime.datetime.strptime(NextTimeStamp, datetimeFormat) + datetime.timedelta(hours=int(Bin))
        NextTimeStamp = datetime.datetime.strftime(NextTimeStamp, datetimeFormat)
        Timelist.append(NextTimeStamp)
    
    print(f'''\n\n\n {run_info_string}_concat.csv\n
           Possible Start Time: {PossibleStartTime}\n
           Possible End Time: {PossibleEndTime}''')

    #  Add possible extra time if the last block of time is within the "ExtraBin" range. 
    diff = datetime.datetime.strptime(PossibleEndTime, datetimeFormat) - datetime.datetime.strptime(NextTimeStamp, datetimeFormat)
    TimeinSeconds = diff.days * 24 * 3600 + diff.seconds
    if(float(ExtraBin)*3600 < TimeinSeconds): 
        Timelist.append(PossibleEndTime) 
        print('        <<<<<<<< Extra Time Bin was Exported >>>>>')   
    print(Timelist)
       

    # Path to concat file. Will be passed to analysis functions later. 
    file_path = os.path.join(IOUTDIR_Concat_files, f"{run_info_string}_concat.csv")
    print(file_path) 
    #loop through all the timestamps per concat file for function_1
    for idx in range(len(Timelist)-1):
        #copied from function_1 call then modified file path, and user input
        
        ## Required Variables! (Start parsetime / End Parsetime)
        columns = ['event_string', 'event_code', 'timestamp', 'counter']

        ## removes leading / trailing whitespaces!! (not in between)  -->
        ## Need to use INPUT functions BEFORE the Tkinter() function (file selection)
        start_parsetime = (Timelist[idx]).strip()
        end_parsetime = (Timelist[idx+1]).strip()
        
        
        # # # # # # Separating INPUT functions from Tkinter function calls
        # # Can't run them together or they'll crash
        
        ## Get the multilevel dataframe and the header information
        multi_df = pd.read_csv(file_path, header=[0, 1], index_col=[0], low_memory=False)
        ## Final Wrapper Function (#7)
        (m_head_dict, m_parsed_dt_df) = final_m_header_and_parsed_dt_df(multi_df, columns, start_parsetime, end_parsetime)
        
        
        ## Returns the actual metric_df and the paradigm for that day (determined by start_parsetime input)
        metric_df, paradigm = return_metric_output_df(m_head_dict, m_parsed_dt_df, start_parsetime)
        

 
        ## Print out the start and end times for the 23hr parsing later
        actual_start_end_times(m_head_dict)
        
        ## Save Format ex: M0228_P5_18-06.csv
        # - M for metric   +  (need to replace "/" with an empty string so that computer doesn't think it's a directory)
        file_title = "M" + start_parsetime[5:10].replace("/","") + "_" + end_parsetime[5:10].replace("/","") + "_" + start_parsetime[-5:-3] + "-" + end_parsetime[-5:-3] + "_" + paradigm
        
        metric_df.to_csv(IOUTDIR_M_files + '/' + file_title + ".csv")
                
        processed_list.append(run_info_string.split("-_-")[-2]+ '  '+ start_parsetime + '   ' + end_parsetime)
        processed_p_list.append(run_info_string.split("-_-")[-2])
        processed_date_list.append(start_parsetime)
    #loop through all the timestamps per concat file for function_8 with latency_choice = response 
    counttwo = 0
    for u in range(len(Timelist)-1):
        
  
        #copied from function_8 call then modified file path, and user input
        
        ### INPUT: concatenated csv data AFTER Step 0  (_concat suffix)
        
        ### IMPT NOTE on the outputted Excel File:
        ## --> last two digits in event_code column will determine if the poke is correct (valid) or incorrect (invalid)
        ## If last two digits are "70": then correct trials
        ## If last two digits are "60": then incorrect trials
        ## Will not contain any omission trials! (by definition of latency, can NOT contain any latency data on omission trials)
        
        ### THIS Script SAVES and also PLOTS!
        
        ## Input Group # & Start-Time & End-Time for Latency Plotting  (PARSING)
        # group_number_input = input("Which group is this? (Ex: g3) ").strip().lower()
        # start_parsetime = input("Enter start-time for LATENCY Plotting (YYYY/MM/DD HH:MM) ").strip()
        # end_parsetime = input("Enter end-time for LATENCY Plotting (YYYY/MM/DD HH:MM) ").strip()
        # paradigm = input('Enter paradigm number (1-6)').strip()
        # paradigm = int(paradigm)
        # latency_choice = input('Enter name of LATENCY you wish to calculate (response, retrieval, initiation)').strip().lower()
        
        group_number_input = ("g5").strip().lower()
        start_parsetime = (Timelist[counttwo]).strip()
        end_parsetime = (Timelist[counttwo+1]).strip()
        #paradigm = (((run_info_string).split("-")[0]).replace('P', '')).strip()
        paradigm = re.split('-|_',run_info_string)[0].replace('P', '').strip()  #  allows P5-5 or P5_5  "-" or "_" labeling 
        paradigm = int(paradigm)
        print('\nParadigm number for latency code (response) is ...', paradigm)
        latency_choice = ('response').strip().lower()
        
        
        if((paradigm == 2) or YesToLatency != 'y'):
            # do not run paradigm 2 (also called P2) because P2 have missing timestamps for the light
            counttwo = counttwo+1
            print('Omitting (response) Latency analysis for P2')
            
        else:
            
            (group, control_list, exp_list, group_subject_list) = det_group_number(group_number_input)


            ##### Actual RUN ##### Actual RUN ##### Actual RUN #####
            
            ## Get the multilevel dataframe and the header information
            multi_df = pd.read_csv(file_path, header=[0, 1], index_col=[0], low_memory=False)
            
            ## Final Wrapper Function (from Step 1 #7)
            (m_head_dict, m_parsed_dt_df) = final_m_header_and_parsed_dt_df(multi_df, columns, start_parsetime, end_parsetime)
            
            ## Latency calculation
            (trial_start, trial_end) = determine_arrays(paradigm, latency_choice)
            
            m_latency_df = multi_latency_concat(m_parsed_dt_df, trial_start, trial_end)
            
            
            ##### SAVE Data for Aggregated Plotting
            
            # Save TO plotting-friendly format!!
            # Objective: In order to concatenate the latency files later!
            
            #save_title = IOUTDIR_Latency_Response + '/' + start_parsetime[:10].replace("/","-") + "_latency_Response.xlsx"
            save_title = IOUTDIR_Latency_Response + '/' + run_info_string.split('-_-')[0] + '_'+ ((start_parsetime.replace('/','_')).replace(' ','-')).replace(':','_') + "_latency_Response.xlsx"
   
            
            plot_df = convert_to_long_format(m_latency_df)
            plot_df['Group'] = group   # Adding Group Information!
            plot_df = create_subject_column(plot_df, group_subject_list)  # Creates subject columns!
            
            # print(plot_df.dtypes)
            
            # Saving Individual latency df to long format!
            plot_df.to_excel(save_title)
            
            
            
            #### PLOTTING!!!  -- Single Day CDF
            
            trial_duration = 5000
            #fig, ax = plot_single_latency_cdf(m_latency_df, start_parsetime, control_list, exp_list, threshold=trial_duration, plot_dropped_box=False, valid_trials=True, horizontal=0.9, port_loc='all')
            
            # final_latency_df.to_excel(title)
            # print(test)
            
            #ax.set_ylabel("Cumulative Density", fontsize=14)
            #ax.set_xlabel("Latency (ms)", fontsize=14)
            
            #plt.tight_layout()
            #plt.show()
            
            ## Save Here!
            # plt.savefig("Whatever title you want")

        
            counttwo = counttwo+1
         
    
    
    #loop through all the timestamps per concat file for function_8 with latency_choice = retrieval 
    counttwo = 0
    for u in range(len(Timelist)-1):
        
  
        #copied from function_8 call then modified file path, and user input
        
        ### INPUT: concatenated csv data AFTER Step 0  (_concat suffix)
        
        ### IMPT NOTE on the outputted Excel File:
        ## --> last two digits in event_code column will determine if the poke is correct (valid) or incorrect (invalid)
        ## If last two digits are "70": then correct trials
        ## If last two digits are "60": then incorrect trials
        ## Will not contain any omission trials! (by definition of latency, can NOT contain any latency data on omission trials)
        
        ### THIS Script SAVES and also PLOTS!
        
        ## Input Group # & Start-Time & End-Time for Latency Plotting  (PARSING)
        # group_number_input = input("Which group is this? (Ex: g3) ").strip().lower()
        # start_parsetime = input("Enter start-time for LATENCY Plotting (YYYY/MM/DD HH:MM) ").strip()
        # end_parsetime = input("Enter end-time for LATENCY Plotting (YYYY/MM/DD HH:MM) ").strip()
        # paradigm = input('Enter paradigm number (1-6)').strip()
        # paradigm = int(paradigm)
        # latency_choice = input('Enter name of LATENCY you wish to calculate (response, retrieval, initiation)').strip().lower()
        
        group_number_input = ("g5").strip().lower()
        start_parsetime = (Timelist[counttwo]).strip()
        end_parsetime = (Timelist[counttwo+1]).strip()
        #paradigm = (((run_info_string).split("-")[0]).replace('P', '')).strip()
        paradigm = re.split('-|_',run_info_string)[0].replace('P', '').strip()  #  allows P5-5 or P5_5  "-" or "_" labeling 
        paradigm = int(paradigm)
        print('\nParadigm number for latency code (retrieval) is ...', paradigm)
        latency_choice = ('retrieval').strip().lower()
        
        
        if((paradigm == 1) or YesToLatency != 'y'):
            # do not run paradigm 2 (also called P2) because P2 have missing timestamps for the light
            counttwo = counttwo+1
            print('Omitting (retrieval) Latency analysis for P1')
            
        else:
            
            (group, control_list, exp_list, group_subject_list) = det_group_number(group_number_input)


            ##### Actual RUN ##### Actual RUN ##### Actual RUN #####
            
            ## Select single csv file (SINGLE DAY)
            multi_df = pd.read_csv(file_path, header=[0, 1], index_col=[0], low_memory=False)

            ## Final Wrapper Function (from Step 1 #7)
            (m_head_dict, m_parsed_dt_df) = final_m_header_and_parsed_dt_df(multi_df, columns, start_parsetime, end_parsetime)
            
            ## Latency calculation
            (trial_start, trial_end) = determine_arrays(paradigm, latency_choice)
            
            m_latency_df = multi_latency_concat(m_parsed_dt_df, trial_start, trial_end)
            
            
            ##### SAVE Data for Aggregated Plotting
            
            # Save TO plotting-friendly format!!
            # Objective: In order to concatenate the latency files later!
            
            #save_title = IOUTDIR_Latency_Retrieval + '/' + start_parsetime[:10].replace("/","-") + "_latency_Retrieval.xlsx"
            save_title = IOUTDIR_Latency_Retrieval + '/' + run_info_string.split('-_-')[0] + '_'+ ((start_parsetime.replace('/','_')).replace(' ','-')).replace(':','_') + "_latency_Retrieval.xlsx"
   
            
            plot_df = convert_to_long_format(m_latency_df)
            plot_df['Group'] = group   # Adding Group Information!
            plot_df = create_subject_column(plot_df, group_subject_list)  # Creates subject columns!
            
            # print(plot_df.dtypes)
            
            # Saving Individual latency df to long format!
            plot_df.to_excel(save_title)
            
            
            
            #### PLOTTING!!!  -- Single Day CDF
            
            trial_duration = 5000
            #fig, ax = plot_single_latency_cdf(m_latency_df, start_parsetime, control_list, exp_list, threshold=trial_duration, plot_dropped_box=False, valid_trials=True, horizontal=0.9, port_loc='all')
            
            # final_latency_df.to_excel(title)
            # print(test)
            
            #ax.set_ylabel("Cumulative Density", fontsize=14)
            #ax.set_xlabel("Latency (ms)", fontsize=14)
            
            #plt.tight_layout()
            #plt.show()
            
            ## Save Here!
            # plt.savefig("Whatever title you want")

        
            counttwo = counttwo+1
         
        
    #loop through all the timestamps per concat file for function_8 with latency_choice = initiation 
    counttwo = 0
    for u in range(len(Timelist)-1):
        
  
        #copied from function_8 call then modified file path, and user input
        
        ### INPUT: concatenated csv data AFTER Step 0  (_concat suffix)
        
        ### IMPT NOTE on the outputted Excel File:
        ## --> last two digits in event_code column will determine if the poke is correct (valid) or incorrect (invalid)
        ## If last two digits are "70": then correct trials
        ## If last two digits are "60": then incorrect trials
        ## Will not contain any omission trials! (by definition of latency, can NOT contain any latency data on omission trials)
        
        ### THIS Script SAVES and also PLOTS!
        
        ## Input Group # & Start-Time & End-Time for Latency Plotting  (PARSING)
        # group_number_input = input("Which group is this? (Ex: g3) ").strip().lower()
        # start_parsetime = input("Enter start-time for LATENCY Plotting (YYYY/MM/DD HH:MM) ").strip()
        # end_parsetime = input("Enter end-time for LATENCY Plotting (YYYY/MM/DD HH:MM) ").strip()
        # paradigm = input('Enter paradigm number (1-6)').strip()
        # paradigm = int(paradigm)
        # latency_choice = input('Enter name of LATENCY you wish to calculate (response, retrieval, initiation)').strip().lower()
        
        group_number_input = ("g5").strip().lower()
        start_parsetime = (Timelist[counttwo]).strip()
        end_parsetime = (Timelist[counttwo+1]).strip()
        #paradigm = (((run_info_string).split("-")[0]).replace('P', '')).strip()
        paradigm = re.split('-|_',run_info_string)[0].replace('P', '').strip()  #  allows P5-5 or P5_5  "-" or "_" labeling 
        paradigm = int(paradigm)
        print('\nParadigm number for latency code (initiation) is ...', paradigm)
        latency_choice = ('initiation').strip().lower()
        
        
        if((paradigm < 5) or YesToLatency != 'y'):
            # do not run paradigm 2 (also called P2) because P2 have missing timestamps for the light
            counttwo = counttwo+1
            print('Omitting (initiation) Latency analysis for P1, P2, P3 and P4')
            
        else:
            
            (group, control_list, exp_list, group_subject_list) = det_group_number(group_number_input)


            ##### Actual RUN ##### Actual RUN ##### Actual RUN #####
            
            ## Select single csv file (SINGLE DAY)
            multi_df = pd.read_csv(file_path, header=[0, 1], index_col=[0], low_memory=False)

            ## Final Wrapper Function (from Step 1 #7)
            (m_head_dict, m_parsed_dt_df) = final_m_header_and_parsed_dt_df(multi_df, columns, start_parsetime, end_parsetime)
            
            ## Latency calculation
            (trial_start, trial_end) = determine_arrays(paradigm, latency_choice)
            
            m_latency_df = multi_latency_concat(m_parsed_dt_df, trial_start, trial_end)
            
            
            ##### SAVE Data for Aggregated Plotting
            
            # Save TO plotting-friendly format!!
            # Objective: In order to concatenate the latency files later!
            
            #save_title = IOUTDIR_Latency_Initiation + '/' + start_parsetime[:10].replace("/","-") + "_latency_Initiation.xlsx"
            save_title = IOUTDIR_Latency_Initiation + '/' + run_info_string.split('-_-')[0] + '_'+ ((start_parsetime.replace('/','_')).replace(' ','-')).replace(':','_') + "_latency_Initiation.xlsx"
            
            plot_df = convert_to_long_format(m_latency_df)
            plot_df['Group'] = group   # Adding Group Information!
            plot_df = create_subject_column(plot_df, group_subject_list)  # Creates subject columns!
            
            # print(plot_df.dtypes)
            
            # Saving Individual latency df to long format!
            plot_df.to_excel(save_title)
            
            
            
            #### PLOTTING!!!  -- Single Day CDF
            
            trial_duration = 5000
            #fig, ax = plot_single_latency_cdf(m_latency_df, start_parsetime, control_list, exp_list, threshold=trial_duration, plot_dropped_box=False, valid_trials=True, horizontal=0.9, port_loc='all')
            
            # final_latency_df.to_excel(title)
            # print(test)
            
            #ax.set_ylabel("Cumulative Density", fontsize=14)
            #ax.set_xlabel("Latency (ms)", fontsize=14)
            
            #plt.tight_layout()
            #plt.show()
            
            ## Save Here!
            # plt.savefig("Whatever title you want")

        
            counttwo = counttwo+1
        
# run step_2 Function call (copied from Step2F_Function)
    
# Select Directory Path
dir_path = IOUTDIR_M_files

# Intermediary (combine all the metrics)
combined_metric_df = combine_daily_metrics(dir_path)

# Filter by location (Default = "Total")
total_df = filter_by_location(combined_metric_df, loc=["Total"])   ## Change Here for Location!


### Valid Code Strings (in a list)
valid_code_string = ["pokes_delay_window","pokes_iti_window","pokes_trial_window","pokes_reward_window","pokes_paradigm_total","trials_omission","trials_incorrect","trials_reward","trials_valid_ports","trials_initiated"]


## df_list will contain ALL the dataframes for each metric
df_list = []
for i, string in enumerate(valid_code_string):
    # print(string)
    df = filter_by_code(total_df, string)
    numeric_df = convert_df_to_numeric(df)
    df_list.append(numeric_df)


## Saving to Excel into separate sheets!
# Setting the unique title
selected_dir_title = os.path.basename(dir_path)

with pd.ExcelWriter(IOUTDIR_Analysis_Output + '/' + selected_dir_title + "_Summary.xlsx") as writer:
    ## For the dataframe saved in df_list,
    ## dataframe gets saved as a separate excel sheet
    ## Sheet name determined by the metric string in the "valid_code_string"

    for i, df in enumerate(df_list):
        # TRANSPOSE HERE!
        df.T.to_excel(writer, f'{valid_code_string[i]}')

     
    

processed_list_forExcel = np.transpose(np.column_stack((processed_p_list, processed_date_list)))

    
end = time.time() 
runtime = (end-start)/60  # in mniutes
 


print('\n\n\n\n\n\n')
#print(temp_file_list)    
#print(np.transpose(temp_file_list))  

print(np.transpose(processed_list))
print('\n\n Thank you,  analysis is completed! ') 
print(f'\n It only took me {runtime} minutes to run the anlaysis!')


print('\n\n For your convenience, paradigm information is stored in variable < processed_list_forExcel > ')

print(f'\n\n Your Analysis Output is located in {OUTDIR}')



    # x = [ 1,2,3,4,5,6,7]
    # count = 0
    # for u in range(len(x)-1):
    #     b = str(x[count]) + ' ' + str(x[count+1]) 
    #     count=count +1
    #     print(b)
    
    
    
    
    
    
    
    #  concat file link to import to function_1
    # IOUTDIR_temp = os.path.join(IOUTDIR_Concat_files, run_info_string+ "_concat.csv")
    # print(IOUTDIR_temp)
    
    # pull information from file_info 

    

    # 
    # SelectedEndtime


# #  test out function 
# def timestwo(x, y):
#     a = (x + y)*2
#     return a
 
# print(timestwo(1,2))   

