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
from matplotlib import rc
# Set default font labels for graphs.
font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 22}
rc('font', **font)

from natsort import natsorted
import sys
import tkinter
import itertools
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
	print(f'I found the following directories: {paradigm_directories}')
	#NB: 'continue_script' will be recycled at various points as a container for user input. 
	continue_script = input('Are these the directories you are looking for (y/n)?    ')
	if continue_script == 'y':
		print('Wonderful! Continuing.')
		files_found = True
	
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
	# If the current variable is Box Number, default to true.
	# It's most likely the one you'll use.
	if var=='Box Number':
		subject_vars_dict[var] = tkinter.BooleanVar(value=True)
	else:
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
group_variables = list(temp_df.index[indexer_array])
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


################################
#    Find and sort M_files     #
################################

# Store M_files_Summary file from each paradigm in a list. Print them as found to verify order.
m_files = []
print('I found the following: \n')
for directory_tree in paradigm_directories:
	m_files.extend(glob(os.path.join(directory_tree,'Analysis_Output', 'M_files_Summary.xlsx')))
	print(m_files[-1])

# Ask user whether it looks like everything was found and it's all in the right order.
# I can't think why they wouldn't be, so I'm leaving it as a simple sys.exit() for now. 
# If there's need, functionality to try to right the wrong in-run can be added later. 
continue_script = input('Does that look right (y/n)?    ')
if continue_script == 'n':
	print("Hm. Ok, well I'll let you figure that out.")
	sys.exit()



################################
#   Create master DataFrames   #
################################
# Index = Subject variable selected above. 
# Columns = multiindex with levels Metric, Paradigm, Day

# We'll hardcode the metrics for now because they should be consistent 
# as long as the extraction code stays the same. 
metrics = ['pokes_delay_window', 'pokes_iti_window', 'pokes_trial_window', 'pokes_paradigm_total',\
		   'trials_omission', 'trials_incorrect', 'trials_reward', 'trials_initiated']

# The name of each paradigm ought to be the last directory in each directory tree.
paradigms = list(map(os.path.basename, paradigm_directories))

# So far the standard seems to be 3 days per paradigm. Initiate the DataFrame with far more than that, 
# and we'll remove any extra at the end. 
days = range(1,11)
# This counter will be used in and after the loop for lopping off anything that isn't used. 
highest_day = 1

column_multiindex = pd.MultiIndex.from_product((metrics, paradigms, days), names=['Metric', 'Paradigm', 'Day'])

# Force consistency in index element format by explicitly setting as strings.
master_DataFrame = pd.DataFrame(index = list(map(str, subject_info_master_df.index)), columns = column_multiindex)
master_DataFrame.sort_index(axis=1, level=['Metric', 'Paradigm', 'Day'], ascending=True, inplace=True)

# Now we populate. 

print('Reading so many excel sheets will take a while. Stay tuned.') 
for paradigm_num, m_file in enumerate(m_files):
	# Both paradigms and m_files were generated by iterating over the same list, so they SHOULD be in the same order.
	paradigm = paradigms[paradigm_num]
	for metric in metrics:
		temp_metric_df = pd.read_excel(m_file, sheet_name=metric, index_col=0, usecols="A,C:L")
		# Index will typically be Box Number in column A. Column B will contain a byproduct of summarizing the M_files
		# and can be skipped. Data from actual run days ought to start at Column C. Grab 10 just to be safe. 
		for subject_id in temp_metric_df.index:
			for day, date in enumerate(temp_metric_df.columns, start=1):
				master_DataFrame.loc[str(subject_id), (metric, paradigm, day)] = temp_metric_df.loc[subject_id, date]
				if day > highest_day:
					highest_day = day

# Take everything up to the highest day. Anything past that is empty. 
master_DataFrame = master_DataFrame.loc[:, (slice(None), slice(None), slice(highest_day))]

# Average across days to create smoothed graphs of metrics across paradigms. 
smoothed_DataFrame = pd.DataFrame(index=subject_info_master_df.index, columns = pd.MultiIndex.from_product((metrics, paradigms), names=['Metric', 'Paradigm']))
smoothed_DataFrame.sort_index(axis=1, level=['Metric', 'Paradigm'], ascending=True, inplace=True)

for metric in metrics:
	for paradigm in paradigms:
		for subject in smoothed_DataFrame.index:
			smoothed_DataFrame.loc[subject, (metric, paradigm)] = master_DataFrame.loc[subject, (metric, paradigm, slice(None))].mean()


# The final DataFrame to make is one that contains grouping information. 
# As an intermediate, we'll add such grouping information as a level underneath metric, tacked on to the end of paradigm. 
paradigms_plus_groups = paradigms.copy()
paradigms_plus_groups.extend(group_variables) 
intermediate_DF_multiindex = pd.MultiIndex.from_product((metrics, paradigms_plus_groups), names=['Metric', 'Paradigm_Group_info'])
# The intermediate DataFrame will then permit the use of the group_by method to easily create the final graphing dataframe. 
intermediate_DataFrame = pd.DataFrame(index=subject_info_master_df.index, columns=intermediate_DF_multiindex)
intermediate_DataFrame.sort_index(axis=1, level=['Metric', 'Paradigm_Group_info'], ascending=True, inplace=True)

# Put all the actual data in at the indices that they have in common. 
intermediate_DataFrame.loc[:, (slice(None), paradigms)] = smoothed_DataFrame.loc[:, :]
# Then iterate over subjects and populate the grouping information. 
for subject in intermediate_DataFrame.index:
	for group_var in group_variables:
		# Places the subject variable value into each Paradigm. 
		intermediate_DataFrame.loc[subject, (slice(None), group_var)] = subject_info_master_df.loc[subject, group_var]

# Finally, create a DataFrame that displays the mean and SEM for each "group" across paradigms within each metric. 
# The number of groups will be determined by the number of grouping variables and the levels of those grouping variables. 
# You will want Main Effects and Interaction comparisons. E.g. Male (all) and Female (all) as well as Male/Cre+ vs. Male/Cre-. 


#Create Index for Graphing DF:
###############################

# Begin this step by determining the relevant levels. These will form the first level of the multi-index index. The multi-index for 
# columns will be that of smoothed_DataFrame. 
graphing_groups = []
all_factor_levels = []
main_effect_legend_labels = {}
# Begin with main effects:
for factor in group_variables:
	levels = set(subject_info_master_df.loc[:, factor])
	all_factor_levels.append(levels)
	main_effect_legend_labels[factor] = list(levels)
	for level in levels:
		graphing_groups.append(level)

# Then get the individual combinations. 
# First by getting a list of lists containing all levels of each factor. 
# all_factor_levels. See above. 
# Then produce all possible combinations of those using itertools. 

# If you have 3 factors, you will want 2 way and 3 way groups. 
# If you have more than 3 factors, get out of here. I'm not dealing with your complexity.
if len(all_factor_levels)>2:	
	# Iterate over pairs of factor lists. 
	for factor_combo in itertools.combinations(all_factor_levels, 2):
		# Then iterate over all combinations of the items in those lists.	
		for group_combo in itertools.product(*factor_combo):
			# group_combo will be a tuple. Store it as a string with '_' separating factor levels.
			graphing_groups.append('_'.join(group_combo))

# Finally, you'll want all possible combinations of factor levels, regardless of factor number. 
for group_combo in itertools.product(*all_factor_levels):
	graphing_groups.append('_'.join(group_combo))

# Create Graphing DF:
#######################
# This whole section is pretty sloppy. It reuses too much of the same logic as above, which feels inefficient. 

graphing_group_index = pd.MultiIndex.from_product([graphing_groups, ['Mean', 'SEM']], names=['Group', 'Stat'])

graphing_DataFrame = pd.DataFrame(index = graphing_group_index, columns = smoothed_DataFrame.columns)
# Columns are already sorted because we recycled from smoothed_DataFrame. 
graphing_DataFrame.sort_index(axis=0, level=['Group', 'Stat'], ascending=True, inplace=True) # Still sort index.

# This bit is hacky, but for groupby().mean() to work, you cant have 'object' dtypes.
# given the complexity of the multi-index and the varying types, this is the simplest
# way that I can think of to get the typing right. 

retyping_dict = list(itertools.product(*[paradigms, ['float64']]))
retyping_dict.extend(list(itertools.product(*[group_variables], ['category'])))
retyping_dict = dict(retyping_dict)

two_way_effect_legend_labels = {}
for metric in metrics:
	# Pull all levels of the Paradigm_Group_info for a given metric as floats and categories. 
	temp_DataFrame = intermediate_DataFrame.loc[:, metric].astype(retyping_dict)
	
	# As before, begin by iterating over levels of individual factors. 
	for factor in group_variables:
		# Group the temporary dataframe by the current grouping variable and perform the operations of interest on it. 
		grouped_means = temp_DataFrame.groupby(factor).mean()
		grouped_SEM = temp_DataFrame.groupby(factor).sem()
		for level in set(subject_info_master_df.loc[:, factor]):
			# Then get the actual values (as an array) for each level. 
			graphing_DataFrame.loc[(level, 'Mean'), (metric)] = grouped_means.loc[level].values 
			graphing_DataFrame.loc[(level, 'SEM'), (metric)] = grouped_SEM.loc[level].values 

	# Next we need to get the combos. 
	if len(all_factor_levels)==2:
		# First we'll do the simple one. 
		big_grouped_mean = temp_DataFrame.groupby(group_variables).mean()
		big_grouped_SEM = temp_DataFrame.groupby(group_variables).sem()
		# big_grouped_mean will be a df with a multi-index. 
		for group_combo in big_grouped_mean.index:
			# The index in graphing_DataFrame is a string, so convert the multiindex tuple to that.
			str_group_combo = '_'.join(group_combo)
			# Make sure you got them in the right order by checking against the list used to create 
			# the index for graphing_DataFrame.
			if str_group_combo not in graphing_groups:
				# if it's not there, try flipping the tuple by indexing in reverse.
				str_group_combo = '_'.join(group_combo[::-1])
			graphing_DataFrame.loc[(str_group_combo, 'Mean'), (metric)] = big_grouped_mean.loc[group_combo].values
			graphing_DataFrame.loc[(str_group_combo, 'SEM'), (metric)] = big_grouped_SEM.loc[group_combo].values

			# This will come in handy for graphing later.
			two_way_effect_legend_labels[str_group_combo] = group_combo
	else:
		# Put a holder in until we figure out how to deal with this.
		print("Sorry, I'm not yet equipped to graph 3 factors. Coming soon!")



# Save all your dataframes before moving on to graphing. 

master_DataFrame.to_csv('All_Animals_Over_All_Days.csv')
intermediate_DataFrame.to_csv('All_Animals_Smoothed_Over_Paradigms.csv')
graphing_DataFrame.to_csv('Group_Means_and_SEMS.csv')

################################
#   Graph individual Behavior  #
################################

for metric in metrics:
	# Begin by making the overall multi-way effect graph (i.e. graph the average of each group)
	plt.figure(metric, figsize=(20, 15))
	metric_legend_dict = {'Handles': [], 'Labels': []} 
	for grp in two_way_effect_legend_labels.keys():
		tmp_handle = plt.errorbar(x = range(len(paradigms)), y=graphing_DataFrame.loc[(grp, 'Mean'), (metric)], yerr=graphing_DataFrame.loc[(grp, 'SEM'), (metric)])
		metric_legend_dict['Handles'].append(tmp_handle)
		metric_legend_dict['Labels'].append(grp)

	
	# Pretty up the graphs by adding labels to the axes
	plt.xticks(range(len(paradigms)), paradigms, rotation=-45)
	plt.xlabel('Paradigm')
	plt.title(metric)

	# Label the lines using the list of handles generated during graphing (above)	
	plt.legend(metric_legend_dict['Handles'], metric_legend_dict['Labels'])
	
	# Save the figure to the current file.
	plt.savefig(f'{metric}_Two_Way_Effect.png')
	plt.close('all')

	# Do the above for each main effect. (i.e. iterate over factors and graph the average of each level, collapsing across other factors.)
	for factor in main_effect_legend_labels.keys():
		factor_legend_dict = {'Handles': [], 'Labels': []} 
		plt.figure(factor, figsize=(20, 15))
		for level in main_effect_legend_labels[factor]:
			tmp_handle = plt.errorbar(x = range(len(paradigms)), y=graphing_DataFrame.loc[(level, 'Mean'), (metric)], yerr=graphing_DataFrame.loc[(level, 'SEM'), (metric)])
			factor_legend_dict['Handles'].append(tmp_handle)
			factor_legend_dict['Labels'].append(level)
		
		plt.xticks(range(len(paradigms)), paradigms, rotation=-45)
		plt.xlabel('Paradigm')
		plt.title(metric)	
		
		plt.legend(factor_legend_dict['Handles'], factor_legend_dict['Labels'])
		
		plt.savefig(f'MainEffectOf{factor}_on{metric}.png')
		plt.close('all')
	
