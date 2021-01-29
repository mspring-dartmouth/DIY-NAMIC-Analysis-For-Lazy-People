#!/usr/bin/env python3

'''
Problem: I would like to be able to quickly and easily generate summary figures of different dependent variables
		 over the course of multiple paradigms. I would like to be able to produce these graphs for both individuals 
		 and for groups. 

Solution: This script will generate graphs and will have two primary processes: first, it will extract group information
		  for all animals in the run. Second, it will extract the processed data from M_file_Summary.xlsx for each phase
		  and graph dependent variables over the course of the entire run. 
Considerations: 
		The script should be able to determine which phases have been run so far and flexibly determine which DVs to graph. 
		It should also be able to accept user input and only process a subset of Phases specified at execution. 
		The ultimate output of the script should be a set of saved figures and sorted spreadsheets that will be conducive to 
		performing statistical analysis. 
		Ultimately, if this script proves useful, GUI functionality should be added. 
'''

import os
from glob import glob

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from natsort import natsorted
import sys
import Tkinter_Selection_Ka_Modified as gui_select
import tkinter



################################
# Extract subject data from P1 #
################################


# Find the output directories for each paradigm. 
# While it assumes that these are named after the paradigms
# and all stored in the same directory, GUI selection is triggered
# if the actual organization differs. 


# We'll make sure that we get these files using a sort of do, while loop. 
files_found = False

# Start looking in the current directory for folders named after paradigms.
base_directory = os.path.abspath(os.path.curdir)
search_pattern = 'P[1-6]*'

# Track how many times the while loop runs to prevent infinite loop.
run_count = 0
while not files_found:
	# If 3 attempts isn't finding the right folders something is seriously wrong. 
	if run_count == 3:
		print('There seems to be something wrong. Exiting so you can debug.')
		sys.exit()

	# Generate a search path, find, and sort the directories. 
	search_path = os.path.join(base_directory, search_pattern)
	paradigm_directories = glob(search_path)
	paradigm_directories = natsorted(paradigm_directories)

	# Check whether these are the directories the user wants. If yes, continue ...
	print(f'I found the following directories: {paradigm_directories}')
	#NB: 'continue_script' will be recycled at various points as a container for user input. 
	continue_script = input('Are these the directories you are looking for (y/n)?    ')
	if continue_script == 'y':
		print('Wonderful! Continuing.')
		files_found = True
		continue
	
	# If no, try to figure out why (i.e. ask for new base_directory or new search_pattern.)
	elif continue_script == 'n':
		print(f'Hm. I searched {search_path} for {search_pattern}.')
		new_dir = input('Would you like to check a different directory (y/n)?    ')
		if new_dir == 'y':
			base_directory = gui_select.select_single_dir()
		new_search_pat = input('Would you like to use a different search pattern (y/n)?    ')
		if new_search_pat == 'y':
			search_pattern = input('Enter new search pattern:    ')

	run_count+=1

# Once the master folders are found, navigate to the bottom of a tree in one of them to find text
# files containing subject data. 

if 'P1' in (list(map(os.path.basename, paradigm_directories))):
	print(f'Searching P1{os.path.sep} for Rearranged_Data{os.path.sep}[DIRECTORY_CONTAINING_TEXTFILES]')
	path_to_raw_data = glob(os.path.join(base_directory, 'P1', 'Rearranged_Data', 'P1-_-*'))
	
	# If there is more than 1 paradigm file, ask user to select which one they'd like to use. 
	if len(path_to_raw_data)>1:
		print('I found\n')
		for i, dir_name in enumerate(path_to_raw_data):
			print(f'{i}: {dir_name}')
		path_selection = input('Which path would you like to use (enter number)?    ')
		path_to_raw_data = path_to_raw_data[int(path_selection)]
		print(f'Got it! Using {path_to_raw_data}')
	
	# If there are no matching files, let user know that something is wrong. 
	elif len(path_to_raw_data)==0:
		
		# Give user the option to manually select a directory.
		continue_script = input("I didn't find any directories here. Would you like to tell me where to look for\n\
								 DIY-NAMIC data files containing subject information? (y/n)?    ")
		if continue_script == 'y':
			gui_select.select_single_dir()
		# If user declines, quit. 
		else:
			print('Ok. Make sure your data are fully processed and then try running this script again.')
			sys.exit()

	# If neither more nor less than one directory was found, there must be only one directory. 
	# glob.glob always returns a list, so get the one element out of it. 
	else:
		path_to_raw_data = path_to_raw_data[0]

else:
	print('Select a directory containing DIY-NAMIC data files containing subject information.')
	path_to_raw_data = gui_select.select_single_dir()

subject_files = glob(os.path.join(path_to_raw_data, '*.txt'))

# a temporary DataFrame to pull out subject information from a single file. 

temp_df = pd.read_csv(subject_files[0], nrows=15, sep=":", index_col=0, header=None)

try:
	# 0113 is the first event code after the file information in the header.
	first_non_header_idx = temp_df.index.get_loc('0113')
except KeyError:
	# If 0113 isn't in the index, grab a larger chunk and try again
	temp_df = pd.read_csv(subject_files[0], nrows=50, sep=':', index_col=0, header=None)
	first_non_header_idx = temp_df.index.get_loc('0113')

# With first_non_header_idx, grab only the relevant section. 
temp_df = temp_df.iloc[:first_non_header_idx]


# Instantiate a GUI window in the center of the screen
master = tkinter.Tk()
master.eval('tk::PlaceWindow . center')

# Create empty dictionaries to hold the checkbox values. 
subject_vars_dict = {}
group_vars_dict = {}

# Create 2 columns of checkboxes labeled with the selected indices.
tkinter.Label(master, text="Subject Var").grid(row=0, column=0, sticky='W')
tkinter.Label(master, text="Group Vars").grid(row=0, column=1, sticky='W')
for row_num, var in enumerate(temp_df.index, start=1):
	subject_vars_dict[var] = tkinter.BooleanVar()
	group_vars_dict[var] = tkinter.BooleanVar()
	tkinter.Checkbutton(master, variable=subject_vars_dict[var]).grid(row=row_num, column=0, sticky='E')
	tkinter.Checkbutton(master, text=var, variable=group_vars_dict[var]).grid(row=row_num,column=1, sticky='W')
tkinter.Button(master, text='Done', command=master.destroy).grid(row=row_num+1, sticky='W', pady=4)

#Instruct the user to select which variables to use for subject identification and which to use for grouping. 
print('Select one Subject Var and all relevant Grouping Vars.')
tkinter.mainloop()


# So selected, use these variables to construct the skeleton of a dataframe:
# Index: Each row will be a subject, so use the number of data files to set number of rows. 
# Columns: Determined by which variables were checked. 
# Create a boolean indexer array based on the values in group_vars_dict

indexer_array = np.array(list(map(lambda x: group_vars_dict[x].get(), temp_df.index)))
group_variables = temp_df.index[indexer_array]
subject_info_master_df = pd.DataFrame(index = range(len(subject_files)), columns=group_variables)

# Figure out the subject variable by checking for the one true variable.  
for var in temp_df.index:
	if subject_vars_dict[var].get():
		subject_var = var
		break

#Populate the dataframe by iterating over the files. 
for idx, f in enumerate(subject_files):
	# Take advantage of knowing how long the header is to only grab what's necessary. 
	temp_subject_df = pd.read_csv(f, nrows=first_non_header_idx, sep=":", index_col=0, header=None)
	for group_var in group_variables:
		# By default, the column containing the variable will be 1.
		raw_value = temp_subject_df.loc[group_var, 1]

		# We want to sanitize the raw_value by removing any leading or trailing whitespace (strip()) and 
		# normalizing the capitilization (upper()) before putting it in the dataframe.  
		subject_info_master_df.loc[idx, group_var] = raw_value.strip().upper()

	#Finally, rename the current loc with the subject variable. 

	#Reusing raw_value as a holder.
	raw_value = temp_subject_df.loc[subject_var, 1]
	sanitized_value = raw_value.strip().upper()

	#Use the rename method in place swap out only the specified idx. 
	subject_info_master_df.rename(index={idx: sanitized_value}, inplace=True)

subject_info_master_df.to_csv('Subject_Data.csv')

print(subject_info_master_df)
continue_script = input('Does this look accurate (y/n)?    ')
if continue_script=='n':
	sys.exit()

print('Excellent! Continuing to analysis.')