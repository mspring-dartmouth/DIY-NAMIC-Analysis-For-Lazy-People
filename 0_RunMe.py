#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 25 15:07:10 2020

@author: Ichimaru
"""


#from Step_0_Settings import *    # import everything
from Step0a_file_concatenate import *
from Step1a_timeframe_parsing import *
from Step1c_paradigm_metrics import *
from Step2a_combine_and_categorize_by_metrics import *
from Step8b_latency import *
from Tkinter_Selection_Ka_Modified import select_all_files_in_directory
from Tkinter_Selection_Ka_Modified import select_all_files_in_directory_works_with_RunMe
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


# Bin needs to be in hours.  To do minutes,  change line 245
print('Files with acquisition time less than the user defined analysis bin size will <<NOT>> be analyzed even though the files will still be sorted')
Bin = input ('What is the analysis bin size in hours? \n(Integer input, lab default is "23")\n\n')
ExtraBin = input('There are residual time leftover in the end of the files.  Select a bin size threshold (in hours) to export those leftover time or type in the same bin size again if you don"t want those residual times. \n(Integer/Float input, lab default is "15") \n\n ')
YesToLatency = input ('\n We will export the count data.\n However, latency data with small analysis time window (e.g. 2 hrs) can cause errors.\n Do you also want to export latency data? (y/n).) )\n\n')

print('\n\n Where is your data? (Please select Path from opened window) ')

# # Directory Selection
(files_list, selected_dir_title) = select_all_files_in_directory()
box_numbers = get_box_numbers(files_list)
file_count = len(files_list)
time.sleep(2) # add some delay time
print('\n Thank you,  I found %s text file(s)' % (file_count))
time.sleep(2) # add some delay time

if len(files_list) == 0:
    print('\n Please try again.  We are looking for data files in ".txt" format ')
    time.sleep(5)
    sys.exit() # kill program 
    
    
time.sleep(2) # add some delay time
print('\n Where should we save the analysis files? (Please select Path)')
## Pick the file path! (single file (output from Step 0)
file_path = select_single_dir()
time.sleep(2) # add some delay time
print('\n Thank you!')



OUTDIR = os.path.join(file_path, 'DIY-NAMIC_Analysis_Output')  # Put data files into folders

if os.path.isdir(OUTDIR): #  remove previous ananlysis folder if in the same location
    print('\n I detected analysis folder from previous run. The folder "DIY-NAMIC_Analysis_Output" will be replace.  ')
    shutil.rmtree(OUTDIR)


if not os.path.isdir(OUTDIR):  #  only create output folder if output link does not already exist
    os.mkdir(OUTDIR)
    
    IOUTDIR_Rerranged_Data = os.path.join(OUTDIR, 'Rerranged_Data')  # Path for creating individual particpant output folder for saving data
    if not os.path.isdir(IOUTDIR_Rerranged_Data):  # only creat output folder if output link  does not exist 
        os.mkdir(IOUTDIR_Rerranged_Data)
    
    IOUTDIR_Analysis_Output = os.path.join(OUTDIR, 'Analysis_Output')  # Path for creating individual particpant output folder for saving data
    if not os.path.isdir(IOUTDIR_Analysis_Output):  # only creat output folder if output link  does not exist 
        os.mkdir(IOUTDIR_Analysis_Output)
file_name =[]
for i in range(file_count):
    full_path = files_list[i]
    #file_name.append(full_path.split("/")[-1])  # File name is always the last in the list
    #file_name.append(full_path.split("\\")[-1])  # File name is always the last in the list # Modified for Windows Computer
    file_name.append(re.split(r'/|\\', full_path)[-1])

print('\n\n Your Analysis Output will be located in %s' % OUTDIR)
print('\n Please wait while we export the data')
start = time.time()  #  for calculating runtime 






varname = []
stop_script = 0
varname.extend(['Start Date', 'Start Time', 'Mouse Line', 'Experiment', 'Paradigm', 'Group', 'Sex', 'Subject', 'Box Number', '0113']) # dictionary for file info
varname.extend(['7070', '8070','9070','5521']) # inintal timestamps
varname.extend(['End Date', 'End Time'])


#create dictionary 

file_info = defaultdict(list)
for xx in range(file_count):  # go through each file 

    temp_file_info = {}
    col_names = ['event_code', 'timestamp', 'counter'] # For TIR (Groups 1,2)
    df = pd.read_csv(files_list[xx], sep=":", header=None, names=col_names)
    
    
    for x in range(len(varname)): # go through each variable
        error = 1 # make sure there is no missing information
        for i in range(len(df)): # searh for variable keywords within each file
            if (varname[x]== df['event_code'][i]): 
                error = 0  # found the timestamp means no error
                temp_file_info[varname[x]]= df['timestamp'][i]
                break  #  terminates loop after finding the first event 
                
        if (error == 1 ):
            stop_script = 1
            print('\n There is missing information in "%s" for text file \n "%s" ' % (varname[x], file_name[xx]))
            temp_file_info[varname[x]]= 'NaN'  #  Space holder for when data is missing 
            
    
    #append individual file information to overall file information
    for j in varname:
        file_info[j].append(temp_file_info[j])


if (stop_script == 1):
    print('\n Sorry, we have to stop the analysis.  There are missing informations in the data file(s).  You need to fix the above file(s) before proceeding. ')
    sys.exit()  # exit the program
    
    
    
#  Create new folders to organize data 
temp_file_list = []

for j in range(file_count):
    temp_file_list.append(file_info['Paradigm'][j]+ '-_-'+ file_info['Start Date'][j])

temp_item_list = list(Counter(temp_file_list).keys())
no_space_temp_item_list = []  # remove spacings for the file names
final_temp_item_list = []  # remove - for the file names

for k in range(len(temp_item_list)):
    no_space_temp_item_list.append(temp_item_list[k].replace(' ', ''))

for k in range(len(temp_item_list)):
    final_temp_item_list.append(no_space_temp_item_list[k].replace('/', '_'))

for i in range(len(temp_item_list)):
    
    IOUTDIR_temp = os.path.join(IOUTDIR_Rerranged_Data, final_temp_item_list[i])  # Path for creating individual particpant output folder for saving data
    if not os.path.isdir(IOUTDIR_temp):  # only creat output folder if output link  does not exist 
        os.mkdir(IOUTDIR_temp)

#  Copy files to new rerrange folder 
for j in range(file_count):
    IOUTDIR_temp = os.path.join(IOUTDIR_Rerranged_Data, (temp_file_list[j].replace(' ', '')).replace('/', '_')+'/'+file_name[j])
    shutil.copyfile(files_list[j],IOUTDIR_temp )
    


#  run Step0F_Function_Calls on all the generated folders
IOUTDIR_Concat_files = os.path.join(IOUTDIR_Analysis_Output, 'Concat_files')  # Path for creating individual particpant output folder for saving data
if not os.path.isdir(IOUTDIR_Concat_files):  # only create output folder if output link  does not exist 
    os.mkdir(IOUTDIR_Concat_files)
for k in range(len(temp_item_list)):
    IOUTDIR_temp = os.path.join(IOUTDIR_Rerranged_Data, final_temp_item_list[k])
    
    #  modified from Step0F_Function_Calls 
    # # Directory Selection
    (files_list, selected_dir_title) = select_all_files_in_directory_works_with_RunMe(IOUTDIR_temp)
    box_numbers = get_box_numbers(files_list)

    # # returns multi_df and its future title
    (df, title) = return_multilevel_df_to_csv(files_list, box_numbers, col_names, selected_dir_title)

    # # Saves the dataframe at THIS stage (otherwise Pycharm crashes if I try to save it without returning the df first!)
    #df.to_csv(title + "_concat.csv")
    df.to_csv(IOUTDIR_Concat_files+ '/'+ title + "_concat.csv")


    ################## Path for Subfolders
# file_count
# file_name
# file_info
# final_temp_item_list

IOUTDIR_M_files = os.path.join(IOUTDIR_Analysis_Output, 'M_files')  # Path for creating individual particpant output folder for saving data
if not os.path.isdir(IOUTDIR_M_files):  # only create output folder if output link  does not exist 
    os.mkdir(IOUTDIR_M_files)

IOUTDIR_Latency_Response = os.path.join(IOUTDIR_Analysis_Output, 'Latency_Response')  # Path for creating individual particpant output folder for saving data
if not os.path.isdir(IOUTDIR_Latency_Response):  # only create output folder if output link  does not exist 
    os.mkdir(IOUTDIR_Latency_Response)

IOUTDIR_Latency_Retrieval = os.path.join(IOUTDIR_Analysis_Output, 'Latency_Retrieval')  # Path for creating individual particpant output folder for saving data
if not os.path.isdir(IOUTDIR_Latency_Retrieval):  # only create output folder if output link  does not exist 
    os.mkdir(IOUTDIR_Latency_Retrieval)

IOUTDIR_Latency_Initiation = os.path.join(IOUTDIR_Analysis_Output, 'Latency_Initiation')  # Path for creating individual particpant output folder for saving data
if not os.path.isdir(IOUTDIR_Latency_Initiation):  # only create output folder if output link  does not exist 
    os.mkdir(IOUTDIR_Latency_Initiation)

processed_list = []
processed_p_list = []
processed_date_list = []

for j in range(len(final_temp_item_list)): # run through each concat file
    
    
    
    # split final_temp_item_list
    TempParadigm = final_temp_item_list[j].split("-_-")[-2]
    TempDate =  (final_temp_item_list[j].split("-_-")[-1]).replace('_', '/')
    
     # grab individual csv header info for each concat file
    TempStartDate = []
    TempStartTime = []
    TempEndDate = []
    TempEndTime = []
    

    for i in range(file_count):
        if(((file_info['Start Date'][i]).replace(' ', '') == TempDate) & ((file_info['Paradigm'][i]).replace(' ', '') == TempParadigm)): #  copy vales from file_info if paradigm and date matches 
            
            TempStartDate.append((file_info['Start Date'][i]).replace(' ', ''))
            TempStartTime .append((file_info['Start Time'][i]).replace(' ', ''))
            TempEndDate.append((file_info['End Date'][i]).replace(' ', ''))
            TempEndTime.append((file_info['End Time'][i]).replace(' ', ''))
            
            
            
            
            
    #find the latest start time and earliest end time 
    
    datetimeFormat = '%Y/%m/%d %H:%M'
    ReferenceTime = TempStartDate[0].split("/")[-1] + '/' + TempStartDate[0].split("/")[-3] + "/" + TempStartDate[0].split("/")[-2] + ' '+ '00:00'
    TempDurationSeconds = []
    for k in range(len(TempStartDate)):
        TestTime = TempStartDate[k].split("/")[-1] + '/' + TempStartDate[k].split("/")[-3] + "/" + TempStartDate[k].split("/")[-2] + ' '+ (TempStartTime[k].replace('-', ':')).split(":")[-3] + ":" + (TempStartTime[k].replace('-', ':')).split(":")[-2]
        diff = datetime.datetime.strptime(TestTime, datetimeFormat)- datetime.datetime.strptime(ReferenceTime, datetimeFormat)
        TimeinSeconds = diff.days *24 * 3600 + diff.seconds
        TempDurationSeconds.append(TimeinSeconds)
    
    P = TempDurationSeconds.index(max(TempDurationSeconds))  # position with earliest start time 
    PossibleStartTime = TempStartDate[P].split("/")[-1] + '/' + TempStartDate[P].split("/")[-3] + "/" + TempStartDate[P].split("/")[-2] + ' '+ (TempStartTime[P].replace('-', ':')).split(":")[-3] + ":" + (TempStartTime[P].replace('-', ':')).split(":")[-2]
    
    TempDurationSeconds = []
    for l in range(len(TempEndDate)):
        TestTime = TempEndDate[l].split("/")[-1] + '/' + TempEndDate[l].split("/")[-3] + "/" + TempEndDate[l].split("/")[-2] + ' '+ (TempEndTime[l].replace('-', ':')).split(":")[-3] + ":" + (TempEndTime[l].replace('-', ':')).split(":")[-2]
        diff = datetime.datetime.strptime(TestTime, datetimeFormat)- datetime.datetime.strptime(ReferenceTime, datetimeFormat)
        TimeinSeconds = diff.days *24 * 3600 + diff.seconds
        TempDurationSeconds.append(TimeinSeconds)
    
    PP = TempDurationSeconds.index(min(TempDurationSeconds))  # position with earliest start time 
    PossibleEndTime = TempEndDate[PP].split("/")[-1] + '/' + TempEndDate[PP].split("/")[-3] + "/" + TempEndDate[PP].split("/")[-2] + ' '+ (TempEndTime[PP].replace('-', ':')).split(":")[-3] + ":" + (TempEndTime[PP].replace('-', ':')).split(":")[-2]
    
 
    # Export data in bin (23 hour blocks), last block is whatever time left until Possible End time. 
    diff = datetime.datetime.strptime(PossibleEndTime, datetimeFormat)- datetime.datetime.strptime(PossibleStartTime, datetimeFormat)
    TimeinSeconds = diff.days *24 * 3600 + diff.seconds
    NumOfHours = TimeinSeconds /3600
    Suggested_Number_of_Run = int(NumOfHours/float(Bin))
    
    
    Timelist = []
    Timelist.append(PossibleStartTime)
    NextTimeStamp = PossibleStartTime
    
    for m in range(Suggested_Number_of_Run):  # subtract one for the begining timestamp 
        NextTimeStamp = datetime.datetime.strptime(NextTimeStamp, datetimeFormat) + datetime.timedelta(hours= int(Bin))
        Timelist.append((str(NextTimeStamp).split(" ")[-2]).replace('-', '/') + ' ' +  (str(NextTimeStamp).split(" ")[-1]).split(":")[-3] + ":" + (str(NextTimeStamp).split(" ")[-1]).split(":")[-2])
        NextTimeStamp =((str(NextTimeStamp).split(" ")[-2]).replace('-', '/') + ' ' +  (str(NextTimeStamp).split(" ")[-1]).split(":")[-3] + ":" + (str(NextTimeStamp).split(" ")[-1]).split(":")[-2])
    
    
    print('\n\n\n', final_temp_item_list[j]+ "_concat.csv")
    print('Possible Start Time:', PossibleStartTime)
    print('Possible End Time:', PossibleEndTime)
    
    

    #  add possible extra time providing that the last block of time is within the "ExtraBin" range. 
    diff = datetime.datetime.strptime(PossibleEndTime, datetimeFormat)- datetime.datetime.strptime(NextTimeStamp, datetimeFormat)
    TimeinSeconds = diff.days *24 * 3600 + diff.seconds
    TimeinMinutes = TimeinSeconds /60
    NumOfHours = TimeinSeconds /3600
    
    
    
    if(float(ExtraBin)*3600 < TimeinSeconds):  # Add the Extra the rest of the time 
        Timelist.append(PossibleEndTime) 
        print('        <<<<<<<< Extra Time Bin was Exported >>>>>')
    
        
    print(Timelist)
       
    # concat file link to import to function_1 and function_8
    IOUTDIR_temp = os.path.join(IOUTDIR_Concat_files, final_temp_item_list[j]+ "_concat.csv")
    print(IOUTDIR_temp) 
     
    #loop through all the timestamps per concat file for function_1
    count = 0
    for u in range(len(Timelist)-1):
        
  
        
        #copied from function_1 call then modified file path, and user input
        
        ## Required Variables! (Start parsetime / End Parsetime)
        columns = ['event_string', 'event_code', 'timestamp', 'counter']

        ## removes leading / trailing whitespaces!! (not in between)  -->
        ## Need to use INPUT functions BEFORE the Tkinter() function (file selection)
        start_parsetime = (Timelist[count]).strip()
        end_parsetime = (Timelist[count+1]).strip()
        
        
        # # # # # # Separating INPUT functions from Tkinter function calls
        # # Can't run them together or they'll crash
        
        
        ## Pick the file path! (single file (output from Step 0)
        file_path = select_single_file(IOUTDIR_temp)
        
        ## Get the multilevel dataframe and the header information
        multi_df = get_multi_df(file_path)
        
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
                

        
        count = count+1
        processed_list.append(final_temp_item_list[j].split("-_-")[-2]+ '  '+ start_parsetime + '   ' + end_parsetime)
        processed_p_list.append(final_temp_item_list[j].split("-_-")[-2])
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
        #paradigm = (((final_temp_item_list[j]).split("-")[0]).replace('P', '')).strip()
        paradigm = re.split('-|_',final_temp_item_list[j])[0].replace('P', '').strip()  #  allows P5-5 or P5_5  "-" or "_" labeling 
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
            
            ## Select single csv file (SINGLE DAY)
            #file_path = select_single_file(IOUTDI23R_temp)
            file_path = IOUTDIR_temp
            
            ## Get the multilevel dataframe (from Step 1)
            multi_df = get_multi_df(file_path)
            
            ## Final Wrapper Function (from Step 1 #7)
            (m_head_dict, m_parsed_dt_df) = final_m_header_and_parsed_dt_df(multi_df, columns, start_parsetime, end_parsetime)
            
            ## Latency calculation
            (trial_start, trial_end) = determine_arrays(paradigm, latency_choice)
            
            m_latency_df = multi_latency_concat(m_parsed_dt_df, trial_start, trial_end)
            
            
            ##### SAVE Data for Aggregated Plotting
            
            # Save TO plotting-friendly format!!
            # Objective: In order to concatenate the latency files later!
            
            #save_title = IOUTDIR_Latency_Response + '/' + start_parsetime[:10].replace("/","-") + "_latency_Response.xlsx"
            save_title = IOUTDIR_Latency_Response + '/' + final_temp_item_list[j].split('-_-')[0] + '_'+ ((start_parsetime.replace('/','_')).replace(' ','-')).replace(':','_') + "_latency_Response.xlsx"
   
            
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
        #paradigm = (((final_temp_item_list[j]).split("-")[0]).replace('P', '')).strip()
        paradigm = re.split('-|_',final_temp_item_list[j])[0].replace('P', '').strip()  #  allows P5-5 or P5_5  "-" or "_" labeling 
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
            #file_path = select_single_file(IOUTDI23R_temp)
            file_path = IOUTDIR_temp
            
            ## Get the multilevel dataframe (from Step 1)
            multi_df = get_multi_df(file_path)
            
            ## Final Wrapper Function (from Step 1 #7)
            (m_head_dict, m_parsed_dt_df) = final_m_header_and_parsed_dt_df(multi_df, columns, start_parsetime, end_parsetime)
            
            ## Latency calculation
            (trial_start, trial_end) = determine_arrays(paradigm, latency_choice)
            
            m_latency_df = multi_latency_concat(m_parsed_dt_df, trial_start, trial_end)
            
            
            ##### SAVE Data for Aggregated Plotting
            
            # Save TO plotting-friendly format!!
            # Objective: In order to concatenate the latency files later!
            
            #save_title = IOUTDIR_Latency_Retrieval + '/' + start_parsetime[:10].replace("/","-") + "_latency_Retrieval.xlsx"
            save_title = IOUTDIR_Latency_Retrieval + '/' + final_temp_item_list[j].split('-_-')[0] + '_'+ ((start_parsetime.replace('/','_')).replace(' ','-')).replace(':','_') + "_latency_Retrieval.xlsx"
   
            
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
        #paradigm = (((final_temp_item_list[j]).split("-")[0]).replace('P', '')).strip()
        paradigm = re.split('-|_',final_temp_item_list[j])[0].replace('P', '').strip()  #  allows P5-5 or P5_5  "-" or "_" labeling 
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
            #file_path = select_single_file(IOUTDI23R_temp)
            file_path = IOUTDIR_temp
            
            ## Get the multilevel dataframe (from Step 1)
            multi_df = get_multi_df(file_path)
            
            ## Final Wrapper Function (from Step 1 #7)
            (m_head_dict, m_parsed_dt_df) = final_m_header_and_parsed_dt_df(multi_df, columns, start_parsetime, end_parsetime)
            
            ## Latency calculation
            (trial_start, trial_end) = determine_arrays(paradigm, latency_choice)
            
            m_latency_df = multi_latency_concat(m_parsed_dt_df, trial_start, trial_end)
            
            
            ##### SAVE Data for Aggregated Plotting
            
            # Save TO plotting-friendly format!!
            # Objective: In order to concatenate the latency files later!
            
            #save_title = IOUTDIR_Latency_Initiation + '/' + start_parsetime[:10].replace("/","-") + "_latency_Initiation.xlsx"
            save_title = IOUTDIR_Latency_Initiation + '/' + final_temp_item_list[j].split('-_-')[0] + '_'+ ((start_parsetime.replace('/','_')).replace(' ','-')).replace(':','_') + "_latency_Initiation.xlsx"
            
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
        df.T.to_excel(writer, '%s' % valid_code_string[i])  ## %s means the substitute is a "string" (data type)

     
    

processed_list_forExcel = np.transpose(np.column_stack((processed_p_list, processed_date_list)))

    
end = time.time() 
runtime = (end-start)/60  # in mniutes
 


print('\n\n\n\n\n\n')
#print(temp_file_list)    
#print(np.transpose(temp_file_list))  

print(np.transpose(processed_list))
print('\n\n Thank you,  analysis is completed! ') 
print('\n It only took me %f minutes to run the anlaysis!' %(runtime))


print('\n\n For your convenience, paradigm information is stored in variable < processed_list_forExcel > ')

print('\n\n Your Analysis Output is located in %s' % OUTDIR)



    # x = [ 1,2,3,4,5,6,7]
    # count = 0
    # for u in range(len(x)-1):
    #     b = str(x[count]) + ' ' + str(x[count+1]) 
    #     count=count +1
    #     print(b)
    
    
    
    
    
    
    
    #  concat file link to import to function_1
    # IOUTDIR_temp = os.path.join(IOUTDIR_Concat_files, final_temp_item_list[j]+ "_concat.csv")
    # print(IOUTDIR_temp)
    
    # pull information from file_info 

    

    # 
    # SelectedEndtime


# #  test out function 
# def timestwo(x, y):
#     a = (x + y)*2
#     return a
 
# print(timestwo(1,2))   

