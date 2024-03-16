# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 22:17:35 2024

@author: rinan
"""

import pandas as pd
import numpy as np


def reapportion_students(full_sabs_dict, my_census, merge_sabs_sdd):
    data = [(block_num, ncessch) for block_num, ncessch in full_sabs_dict.items()]
    full_sabs_df = pd.DataFrame(data, columns=['block_num', 'ncessch'])
    # list of unique ncessch in the leaid
    unique_ncessch = full_sabs_df['ncessch'].unique().tolist()# Initialize an empty DataFrame for combining all apportioned_students data across schools
    # initialize dataframe to store results of loop
    apportioned_students_df = pd.DataFrame()
    # for each ncessch, reapportion students by race from school to blocks
    for ncessch in unique_ncessch:
        # Find rows in full_sabs_df where 'ncessch' matches the current ncessch and get the 'block_num' values
        block_list = full_sabs_df[full_sabs_df['ncessch'] == ncessch]['block_num'].tolist()
        # Keep only the census race data that pertains to blocks in the block list.
        census_filtered = my_census[my_census['geoid'].isin(block_list)]
        # Keep only the school data pertaining to this school
        sdd_filtered = merge_sabs_sdd[merge_sabs_sdd['ncessch'] == ncessch ]
        
        # # Now, reapportion students from each school to blocks by race
        # Define races to loop over
        races = ['blackpop', 'whitepop', 'hispanicpop', 'asianpop', 'nativeamericanpop', 'nhpipop', 'multiracepop']
        school_enrollments = {
            'blackpop': sdd_filtered['enrollblack'].values[0],
            'whitepop': sdd_filtered['enrollwhite'].values[0],
            'hispanicpop': sdd_filtered['enrollhispanic'].values[0],
            'asianpop': sdd_filtered['enrollasian'].values[0],
            'nativeamericanpop': sdd_filtered['enrollaian'].values[0],
            'nhpipop': sdd_filtered['enrollnhpi'].values[0],
            'multiracepop': sdd_filtered['enrollmultirace'].values[0]
         }   
        # Initialize a DataFrame to store apportioned students
        apportioned_students = pd.DataFrame(index=census_filtered.index, columns=races + ['total'])
        apportioned_students['geoid'] = census_filtered['geoid'].values
        apportioned_students['ncessch'] = ncessch
    
        # loop through each race
        for race in races:
            # Total number of students from race i at school j
            total_students = school_enrollments[race]
            # Calculate what percentage of students from school j of race i comes from block k
            percentages = census_filtered[race] / census_filtered[race].sum()
            
            # Calculate expected number of students for each block
            expected_students = np.round(percentages * total_students).fillna(0).astype(int)
            
            # Adjust for rounding issues to match total exactly by using numpy to probabilistically adjusts the apportioned students to ensure that the total number of students by race assigned to blocks matches the school's enrollment figures for that race.
    
            # diff between total number of students at the school and the expected value of students across all races
            difference = total_students - expected_students.sum()
            # if there is a discrepancy between actual total number of students and expected value:
            if difference != 0:
                # randomly selected block indices to adjust based on the size of the discrepancy (abs(difference)) and the distribution of percentages, which indicate how students are spread across blocks
                adjustments = np.random.choice(expected_students.index, abs(difference.astype(int)), replace=True, p=percentages.values)
                # iterates over the randomly chosen block indices
                for index in adjustments:
                    # adjusts the num of students in the block by adding or subtracting 1 student, based on the sign of the difference
                    expected_students[index] += np.sign(difference.astype(int))
            # save the reapportioned number of students per block as a new column in the df for the given race
            apportioned_students[race] = expected_students
        
        # sum the total across all races
        apportioned_students['total'] = apportioned_students[races].sum(axis=1)
        
        # append all data from each school to a single df
        apportioned_students_df = pd.concat([apportioned_students_df, apportioned_students.reset_index(drop=True)], ignore_index=True)
     
    # check that the apportioned students total adds up correctly
    total_enrollment = sum(school_enrollments.values())
    apportioned_total_enrollment = apportioned_students['total'].sum()
    print(f"Actual Total Enrollment: {total_enrollment}")
    print(f"Apportioned Total Enrollment: {apportioned_total_enrollment}")
    for race in races:
        apportioned_race_total = apportioned_students[race].sum()
        print(f"Total {race}: {apportioned_race_total} (Expected: {school_enrollments[race]})")
    
    
    # Plot the distribution of races
    # Filter out blocks where the total population is 0
    apportioned_students_nonzero = apportioned_students[apportioned_students['total'] > 0]
    
    return apportioned_students_df, apportioned_students_nonzero


def apportioned_to_dg(apportioned_students_df, bl_dg):
        
    ### now, add apportioned_students df to bl_dg
    # Convert GEOID10 to a string if it's not already, to match the geoid format in apportioned_students
    apportioned_students_df['geoid'] = apportioned_students_df['geoid'].astype(str)
    
    # Iterate through each node in the bl_dg graph
    for node in bl_dg.nodes:
        # Get the GEOID10 of the current node
        geoid10 = bl_dg.nodes[node]['GEOID10']
        
        # Find the matching row in apportioned_students
        matching_row = apportioned_students_df[apportioned_students_df['geoid'] == geoid10]
        
        # If there is a matching row, update the node attributes with the data from apportioned_students
        if not matching_row.empty:
            # Convert matching row to a dictionary and update the node
            # Note: iloc[0] is used because matching_row is a DataFrame and we need the first (and only) row as a Series
            bl_dg.nodes[node].update(matching_row.iloc[0].to_dict())
        
    return bl_dg