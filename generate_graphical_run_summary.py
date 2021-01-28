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
	print('I found the following directories: {paradigm_directories}')
	#NB: 'continue_script' will be recycled at various points as a container for user input. 
	continue_script = input('Are these the directories you are looking for (y/n)?    ')
	if continue_script == 'y':
		print('Wonderful! Continuing.')
		files_found = True
		continue
	
	# If no, try to figure out why (i.e. ask for new base_directory or new search_pattern.)
	else continue_script == 'n':
		print('Hm. I searched {} for {}.')
		new_dir = input('Would you like to check a different directory (y/n)    ?')
		if new_dir == 'y':
			base_directory = gui_select.select_single_dir()
		new_search_pat = input('Would you like to use a different search pattern (y/n)   ?')
		if new_search_pat == 'y':
			search_pattern = input('Enter new search pattern:    ')

	run_count+=1

# Once the master folders are found, navigate to the bottom of a tree in one of them to find text
# files containing subject data. 

if 'P1' in paradigm_directories:
	print(f'Searching P1{os.path.sep} for Rearranged_Data{os.path.sep}[DIRECTORY_CONTAINING_TEXTFILES]')
	path_to_raw_data = glob(os.path.join('P1', 'Rearranged_Data', 'P1-_-*'))
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

	# If neither more than nor less than one directory was found, there must be only one directory. 
	# glob.glob always returns a list, so get the one element out of it. 
	else:
		path_to_raw_data = path_to_raw_data[0]

else:
	print('Select a directory containing DIY-NAMIC data files containing subject information.')
	path_to_raw_data = gui_select.select_single_dir()




