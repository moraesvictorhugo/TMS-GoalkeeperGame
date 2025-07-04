"""
=================================================
Main Analysis Script
=================================================
"""
from modules import analysis
from modules import import_signal
from modules import plot_data
from modules import utils
import numpy as np
import pandas as pd

# """
# ============================================
# STEP 0 - Importing Data and Setting Flags
# ============================================
# """
## Importing processed csv file
file_path = "/home/victormoraes/MEGA/Archive/IBCCF/Projeto Doc/EMT no Jogo do goleiro/Data processing/TMS-GKg_Analysis/data_TMS-GKg/Processed_data/"
file_name = "df_gklab.csv"
df = import_signal.import_csv_data(file_path, file_name)

## Setting flags and filtering data
type_analysis = 'group'                  # "individual" or "group"
volunteer_id = 1                          # adjust according to the volunteer number
remove_familiarization_trials = True      # Remove familiarization trials
lst_excluded_volunteers = []

# Filter data for individual analysis
if type_analysis == 'individual':
    df = df[df["ID_info"] == volunteer_id]

# Exclude volunteers
if type_analysis == 'group':
    df = df[~df['ID_info'].isin(lst_excluded_volunteers)]

# Remove familiarization trials
if remove_familiarization_trials:
    df = df[df['block_info'] != 0]

# Remove non valid MEPs
df.replace(99999, np.nan, inplace=True)

# Replace values in 'response_time_info' that are greater than 1.5 with NaN
df.loc[df['response_time_info'] > 1.5, 'response_time_info'] = np.nan

# Create a new column to categorize TMS pulses
df['tms_pulse'] = df['block_info'].apply(utils.categorize_tms_pulse)

# Create a new column to verify if columns response_info and stochastic_chain_info match
df['result'] = np.where(df['response_info'] == df['stochastic_chain_info'], 'correct', 'incorrect')

# Reset data frame index and create last_was_error column
df = analysis.add_last_was_error(df)

# Create a new column of contexts
df = analysis.create_context_column(df)

# Reorganize data frame
new_order = ['group_info', 'day_info', 'play_info', 'step_info', 'tree_info',
       'ID_info', 'response_time_info', 'response_info',
       'stochastic_chain_info', 'result', 'last_was_error', 'context', 
       'block_info', 'tms_pulse','MEPpp_FDI_µV', 'MEPpp_FDS_µV',
       'relRest_MEPpp_FDI', 'relRest_MEPpp_FDS', 'relMean_MEPpp_FDI',
       'relMean_MEPpp_FDS']

df = df[new_order]

# """
# ============================================
# STEP 1 - Individual Success Rate Analysis
# ============================================
# """
if type_analysis == 'individual':
    # Global success rate analysis
    global_success_rate, _ = analysis.calculate_global_success_rate_individual(df)
    global_success_rate_with_exclusion, _ = analysis.calculate_global_success_rate_with_exclusion_individual(df, exclude_first_last=100)

    # Define Plot parameters
    global_success_rates = [global_success_rate, global_success_rate_with_exclusion]
    global_success_rate_labels = ['Global Success Rate', 'Global Success Rate with Exclusion']
    global_success_rate_colors = ['cornflowerblue', 'limegreen']

    # Call the function
    plot_data.plot_success_rate_individual(global_success_rates, global_success_rate_labels, global_success_rate_colors)

    # Block success rate analysis
    success_rate_block1, success_rate_block2, success_rate_block3, success_rate_block4, success_rate_block5, success_rate_block6 = analysis.calculate_success_rate_by_block_individual(df)

    # Define Plot parameters
    block_success_rates = [success_rate_block1, success_rate_block2, success_rate_block3, success_rate_block4, success_rate_block5, success_rate_block6]
    block_success_rate_labels = ['Block 1', 'Block 2', 'Block 3', 'Block 4', 'Block 5', 'Block 6']

    # Call the function
    plot_data.plot_success_rate_individual(block_success_rates, block_success_rate_labels) #, block_success_rate_colors)

    # Sucess rate with and without TMS
    success_rate_with_tms = np.mean([success_rate_block2, success_rate_block4, success_rate_block6])
    success_rate_without_tms = np.mean([success_rate_block1, success_rate_block3, success_rate_block5])

    # Define Plot parameters
    success_rates = [success_rate_with_tms, success_rate_without_tms]
    success_rate_labels = ['With TMS', 'Without TMS']
    success_rate_colors = ['cornflowerblue', 'limegreen']

    # Call the function
    plot_data.plot_success_rate_individual(success_rates, success_rate_labels, success_rate_colors)


    # ### Noslem criteria analysis to exclude participants

    # # Apply a logit transformation to the data for normalized proportion of correct guesses


    # # Split data in windows


    # # Fit a Least Squares Regression Model


    # # Plot the data


    # # Remove negative slopes individuals in step 0

# """
# ============================================
# STEP 1 - Group Success Rate Analysis
# ============================================
# """
if type_analysis == 'group':
    ### Global success rate analysis
    global_success_rate, std_global_success_rate = analysis.calculate_global_success_rate_group(df)
    global_success_rate_with_exclusion, std_global_success_rate_with_exclusion = analysis.calculate_global_success_rate_with_exclusion_group(df,exclude_first_last=100)

    # Define Plot parameters
    global_success_rate_labels = ['Global Success Rate', 'Global Success Rate with Exclusion']

    # Call the function
    plot_data.plot_success_rate_comparison_group(global_success_rate, global_success_rate_with_exclusion ,global_success_rate_labels)                            

    ### Block success rate analysis
    success_rate_blocks = analysis.calculate_success_rate_by_block_group(df)
    plot_data.plot_success_rates_by_blocks_group(df)
    
    # # Calculating mean values of individuals with and without TMS
    success_rate_mean_NoPulse_Pulse_group = analysis.calculate_means_PulseNopulse(success_rate_blocks)

    # # Plot sucess rate with and without TMS
    plot_data.plot_means_boxplot(success_rate_mean_NoPulse_Pulse_group)

# """
# ============================================
# STEP 2 - Individual Response Times Analysis
# ============================================
# """
if type_analysis == 'individual':
    # Plot RTs by Block
    plot_data.plot_boxplot(df, 'response_time_info', 'block_info', title='Response Times by Block', xlabel='Blocks', ylabel='RTs (s)', figsize=(12, 8), dpi=900, outlier_threshold=1.5)

    # Plot RTs by TMS pulse
    plot_data.plot_boxplot(df, 'response_time_info', 'tms_pulse', title='Response Times by TMS Pulse', xlabel='TMS Pulses', ylabel='RTs (s)', figsize=(12, 8), dpi=900, outlier_threshold=1.5)

    # Get Response Times by Contexts
    RTs_ctx_00, RTs_ctx_10, RTs_ctx_20, RTs_ctx_1, RTs_ctx_2 = analysis.get_variable_by_context(df)

    # Exclude outliers in RTs by Context
    RTs_ctx_00 = [num for num in RTs_ctx_00 if num < 1.5]
    RTs_ctx_10 = [num for num in RTs_ctx_10 if num < 1.5]
    RTs_ctx_20 = [num for num in RTs_ctx_20 if num < 1.5]
    RTs_ctx_1 = [num for num in RTs_ctx_1 if num < 1.5]
    RTs_ctx_2 = [num for num in RTs_ctx_2 if num < 1.5]

    # Combine all RTs into a list of lists
    list_RTs_ctx = [RTs_ctx_00, RTs_ctx_10, RTs_ctx_20, RTs_ctx_1, RTs_ctx_2]

    ######### Plot Response Times by Contexts
    plot_data.create_boxplot_withLists(list_RTs_ctx, title='Boxplot of Response Times by Context', xlabel='Context', ylabel='Response Time (s)', title_fontsize=16, xlabel_fontsize=14, ylabel_fontsize=14)

    ######### Plot RTs with EMT by Context
    rt_pulse_df = df.loc[(df['tms_pulse'] == 'Pulse')]
    RTs_Pulse_ctx_00, RTs_Pulse_ctx_10, RTs_Pulse_ctx_20, RTs_Pulse_ctx_1, RTs_Pulse_ctx_2 = analysis.get_variable_by_context(rt_pulse_df)

    RTs_Pulse_ctx_00 = [num for num in RTs_Pulse_ctx_00 if num < 1.5]
    RTs_Pulse_ctx_10 = [num for num in RTs_Pulse_ctx_10 if num < 1.5]
    RTs_Pulse_ctx_20 = [num for num in RTs_Pulse_ctx_20 if num < 1.5]
    RTs_Pulse_ctx_1 = [num for num in RTs_Pulse_ctx_1 if num < 1.5]
    RTs_Pulse_ctx_2 = [num for num in RTs_Pulse_ctx_2 if num < 1.5]

    list_RTs_Pulse_ctx = [RTs_Pulse_ctx_00, RTs_Pulse_ctx_10, RTs_Pulse_ctx_20, RTs_Pulse_ctx_1, RTs_Pulse_ctx_2]

    # Plot RTs with EMT by Context
    plot_data.create_boxplot_withLists(list_RTs_Pulse_ctx, title='Response Times with TMS by Context', xlabel='Context', ylabel='Response Time (s)', title_fontsize=16, xlabel_fontsize=14, ylabel_fontsize=14)

    ######### Plot RTs without EMT by Context
    rt_NoPulse_df = df.loc[(df['tms_pulse'] == 'noPulse')]
    RTs_NoPulse_ctx_00, RTs_NoPulse_ctx_10, RTs_NoPulse_ctx_20, RTs_NoPulse_ctx_1, RTs_NoPulse_ctx_2 = analysis.get_variable_by_context(rt_NoPulse_df)

    RTs_NoPulse_ctx_00 = [num for num in RTs_NoPulse_ctx_00 if num < 1.5]
    RTs_NoPulse_ctx_10 = [num for num in RTs_NoPulse_ctx_10 if num < 1.5]
    RTs_NoPulse_ctx_20 = [num for num in RTs_NoPulse_ctx_20 if num < 1.5]
    RTs_NoPulse_ctx_1 = [num for num in RTs_NoPulse_ctx_1 if num < 1.5]
    RTs_NoPulse_ctx_2 = [num for num in RTs_NoPulse_ctx_2 if num < 1.5]

    list_RTs_NoPulse_ctx = [RTs_NoPulse_ctx_00, RTs_NoPulse_ctx_10, RTs_NoPulse_ctx_20, RTs_NoPulse_ctx_1, RTs_NoPulse_ctx_2]

    # Plot RTs without EMT by Context
    plot_data.create_boxplot_withLists(list_RTs_NoPulse_ctx, title='Response Times without TMS by Context', xlabel='Context', ylabel='Response Time (s)', title_fontsize=16, xlabel_fontsize=14, ylabel_fontsize=14)

# """
# ============================================
# STEP 2 - Group Response Times Analysis
# ============================================
# """
if type_analysis == 'group':
    
    # Calculate mean response times grouped by ID_info and block_info
    mean_response_times_by_blocks = df.groupby(['ID_info', 'block_info'])['response_time_info'].mean().reset_index()

    # Plot RTs by Block
    plot_data.plot_boxplot(mean_response_times_by_blocks, 'response_time_info', 'block_info', title='Mean Response Times by Block', xlabel='Blocks', ylabel='Response Times (s)', figsize=(10, 6), dpi=600, outlier_threshold=1.5)

    # Calculate mean response times grouped by ID_info and TMS pulse
    mean_response_times_NoPulse_Pulse = df.groupby(['ID_info', 'tms_pulse'])['response_time_info'].mean().reset_index()

    # Plot RTs by TMS pulse
    plot_data.plot_boxplot(mean_response_times_NoPulse_Pulse, 'response_time_info', 'tms_pulse', title='Response Times by TMS Pulse', xlabel='TMS Pulses', ylabel='RTs (s)', figsize=(10, 6), dpi=600, outlier_threshold=1.5)

    ######### Plot RTs by Context
    # Get Mean Response Times by Contexts and Plot   
    mean_response_times_ctx = df.groupby(['ID_info', 'context'])['response_time_info'].mean().reset_index()

    plot_data.boxplot_dataframe_onecategory(
        df=mean_response_times_ctx,
        x= 'context',
        y= 'response_time_info',
        xlabel='context',         
        ylabel='Response Times (s)',     
        title='Mean RTs by Contexts'
    )
    
    ######### Plot RTs with EMT by Context    
    
    # Filter RTs during pulses
    rt_pulse_df = df.loc[(df['tms_pulse'] == 'Pulse')]

    # Get Mean Response Times by Contexts and Plot   
    mean_response_times_pulse_ctx = rt_pulse_df.groupby(['ID_info', 'context'])['response_time_info'].mean().reset_index()

    plot_data.boxplot_dataframe_onecategory(
        df=mean_response_times_pulse_ctx,
        x= 'context',
        y= 'response_time_info',
        xlabel='context',         
        ylabel='Response Times (s)',     
        title='Mean RTs with TMS by Contexts'
    )
    
    ######### Plot RTs without EMT by Context
    
    # FIlter RTs without pulses
    rt_nopulse_df = df.loc[(df['tms_pulse'] == 'noPulse')]

    # Get Mean Response Times by Contexts and Plot   
    mean_response_times_nopulse_ctx = rt_nopulse_df.groupby(['ID_info', 'context'])['response_time_info'].mean().reset_index()

    plot_data.boxplot_dataframe_onecategory(
        df=mean_response_times_nopulse_ctx,
        x= 'context',
        y= 'response_time_info',
        xlabel='context',         
        ylabel='Response Times (s)',     
        title='Mean RTs without TMS by Contexts'
    )
    
    ######### Plot RTs by Context and Previous result
 
    # Get Mean Response Times by Contexts and Plot   
    mean_response_times_ctx_prevresult = df.groupby(['ID_info', 'context', 'last_was_error'])['response_time_info'].mean().reset_index()

    plot_data.boxplot_dataframe_twocategories(
        df=mean_response_times_ctx_prevresult,
        xdata='context',         # Column for x-axis (context)
        ydata='response_time_info',      # Column for y-axis (mean values)
        huedata='last_was_error',# Column for hue (error status)
        xlabel='Contexts',
        ylabel='Response Times (s)',     # Label for y-axis
        title='Mean RTs by Contexts and Previous Result',
        legend_title='Previous Error'
    )
    
    ########## RTs differences Context and Previous Result Analysis 

    # Create a pivot table to calculate mean relMean_MEPpp_FDI for each combination
    pivot_table = pd.pivot_table(mean_response_times_ctx_prevresult,
                                values='response_time_info',
                                index=['ID_info', 'context'],
                                columns='last_was_error',
                                aggfunc='mean',
                                fill_value=0)

    # Calculate the difference between last_was_error categories
    pivot_table['mean_difference'] = pivot_table[1] - pivot_table[0]
    
    # Back to stack structure
    stacked_df = pivot_table[['mean_difference']].reset_index()
    
    # Plot Difference between previous error and success on MEPs by contexts 
    plot_data.boxplotDot_dataframe_onecategory(
        df=stacked_df,
        x= 'context',
        y= 'mean_difference',
        xlabel='Contexts',         
        ylabel='RT error - RT success',     
        title='RTs Mean Difference between Previous Error and Success'
    )
    
    ######### Plot RTs with TMS by Context and Previous result    
    
    # Filter RTs during pulses
    rt_pulse_df = df.loc[(df['tms_pulse'] == 'Pulse')]

    # Get Mean Response Times by Contexts and Plot   
    mean_response_times_pulse_ctx_prevresult = rt_pulse_df.groupby(['ID_info', 'context', 'last_was_error'])['response_time_info'].mean().reset_index()

    plot_data.boxplot_dataframe_twocategories(
        df=mean_response_times_pulse_ctx_prevresult,
        xdata= 'context',
        ydata= 'response_time_info',
        huedata='last_was_error',
        xlabel='Contexts',         
        ylabel='Response Times (s)',     
        title='Mean RTs with TMS by Contexts and Previous Result',
        legend_title='Previous Error'
    )
    
    ########## RTs differences with TMS by Context and Previous Result Analysis 

    # Create a pivot table to calculate mean relMean_MEPpp_FDI for each combination
    pivot_table = pd.pivot_table(mean_response_times_pulse_ctx_prevresult,
                                values='response_time_info',
                                index=['ID_info', 'context'],
                                columns='last_was_error',
                                aggfunc='mean',
                                fill_value=0)

    # Calculate the difference between last_was_error categories
    pivot_table['mean_difference'] = pivot_table[1] - pivot_table[0]
    
    # Back to stack structure
    stacked_df = pivot_table[['mean_difference']].reset_index()
    
    # Plot Difference between previous error and success on MEPs by contexts 
    plot_data.boxplotDot_dataframe_onecategory(
        df=stacked_df,
        x= 'context',
        y= 'mean_difference',
        xlabel='Contexts',         
        ylabel='RT error - RT success',     
        title='RTs Mean Difference with TMS between Previous Error and Success'
    )
    
    
    ######### Plot RTs without EMT by Context and Previous result
    
    # Filter RTs without pulses
    rt_nopulse_df = df.loc[(df['tms_pulse'] == 'noPulse')]

    # Get Mean Response Times by Contexts and Plot   
    mean_response_times_nopulse_ctx_prevresult = rt_nopulse_df.groupby(['ID_info', 'context', 'last_was_error'])['response_time_info'].mean().reset_index()

    plot_data.boxplot_dataframe_twocategories(
        df=mean_response_times_nopulse_ctx_prevresult,
        xdata= 'context',
        ydata= 'response_time_info',
        huedata='last_was_error',
        xlabel='Contexts',         
        ylabel='Response Times (s)',     
        title='Mean RTs without TMS by Contexts and Previous Result',
        legend_title='Previous Error'
    )
    
    ########## RTs differences without TMS by Context and Previous Result Analysis 

    # Create a pivot table to calculate mean relMean_MEPpp_FDI for each combination
    pivot_table = pd.pivot_table(mean_response_times_nopulse_ctx_prevresult,
                                values='response_time_info',
                                index=['ID_info', 'context'],
                                columns='last_was_error',
                                aggfunc='mean',
                                fill_value=0)

    # Calculate the difference between last_was_error categories
    pivot_table['mean_difference'] = pivot_table[1] - pivot_table[0]
    
    # Back to stack structure
    stacked_df = pivot_table[['mean_difference']].reset_index()
    
    # Plot Difference between previous error and success on MEPs by contexts 
    plot_data.boxplotDot_dataframe_onecategory(
        df=stacked_df,
        x= 'context',
        y= 'mean_difference',
        xlabel='Contexts',         
        ylabel='RT error - RT success',     
        title='RTs Mean Difference without TMS between Previous Error and Success'
    )
     
# """
# ============================================
# STEP 3 - Individual MEP Analysis
# ============================================
# """
if type_analysis == 'individual':
    
    # Plot FDI MEPs by Block
    plot_data.plot_boxplot(
        df,
        value_column='MEPpp_FDI_µV',
        group_column='block_info',
        title='Raw MEPs by Block',
        xlabel='Blocks',
        ylabel='MEP amplitude (µV)',
        figsize=(14, 10),
        dpi=300,
        outlier_threshold=1000,
        group_values=[2, 4, 6]
    )

    # Get MEPs by Contexts
    MEPs_ctx_00, MEPs_ctx_10, MEPs_ctx_20, MEPs_ctx_1, MEPs_ctx_2 = analysis.get_variable_by_context(df, col_var=9)

    # Exclude outliers in MEPs by Context
    MEPs_ctx_00 = [num for num in MEPs_ctx_00 if num < 1000]
    MEPs_ctx_10 = [num for num in MEPs_ctx_10 if num < 1000]
    MEPs_ctx_20 = [num for num in MEPs_ctx_20 if num < 1000]
    MEPs_ctx_1 = [num for num in MEPs_ctx_1 if num < 1000]
    MEPs_ctx_2 = [num for num in MEPs_ctx_2 if num < 1000]


    # Combine all MEPs into a list of lists
    list_MEPs_ctx = [MEPs_ctx_00, MEPs_ctx_10, MEPs_ctx_20, MEPs_ctx_1, MEPs_ctx_2]

    # Plot MEPs by Contexts
    plot_data.create_boxplot_withLists(
        list_MEPs_ctx,
        title='Boxplot of FDI MEPs by Context',
        xlabel='Context', 
        ylabel='FDI MEP amplitude (µV)', 
        title_fontsize=16, 
        xlabel_fontsize=14, 
        ylabel_fontsize=14)

# """
# ============================================
# STEP 3 - Group MEP Analysis
# ============================================
# """
if type_analysis == 'group':

    meps_blocks_df = df.loc[(df['tms_pulse'] == 'Pulse')]
    
    ###### Block analysis
    # Calculate mean FDI MEPs grouped by ID_info and block_info
    mean_FDImeps_by_blocks = meps_blocks_df.groupby(['ID_info', 'block_info'])['relMean_MEPpp_FDI'].mean().reset_index()

    # Plot FDI MEPs by Block
    plot_data.plot_boxplot(
        mean_FDImeps_by_blocks,
        value_column='relMean_MEPpp_FDI',
        group_column='block_info',
        title='MEPs by Blocks',
        xlabel='Blocks',
        ylabel='Relative FDI MEPs',
        figsize=(12, 8),
        dpi=600,
        group_values=[2, 4, 6]
    )

    ###### Context Analysis
    
    # Get Mean FDI MEPs relative to mean by Contexts and Plot    
    mean_relmFDImepsmean_ctx = meps_blocks_df.groupby(['ID_info', 'context'])['relMean_MEPpp_FDI'].mean().reset_index()

    plot_data.boxplot_dataframe_onecategory(
        df=mean_relmFDImepsmean_ctx,
        x= 'context',
        y= 'relMean_MEPpp_FDI',
        xlabel='Contexts',         
        ylabel='Relative FDI MEP Amplitude',     
        title='Mean MEPs by Contexts'
    )
    
    # Get Mean FDI MEPs relative to rest by Contexts and Plot    
    mean_relrFDImepsmean_ctx = meps_blocks_df.groupby(['ID_info', 'context'])['relRest_MEPpp_FDI'].mean().reset_index()

    plot_data.boxplot_dataframe_onecategory(
        df=mean_relrFDImepsmean_ctx,
        x= 'context',
        y= 'relRest_MEPpp_FDI',
        xlabel='Contexts',         
        ylabel='Relative FDI MEP Amplitude',     
        title='Mean MEPs by Contexts'
    )
    
    
    ###### Context and Previous Result Analysis
    
    # Get Mean FDI MEPs by Contexts and Previous Result and Plot    
    mean_FDImeps_ctx_prevresult = meps_blocks_df.groupby(['ID_info', 'context', 'last_was_error'])['relMean_MEPpp_FDI'].mean().reset_index()

    plot_data.boxplot_dataframe_twocategories(
        df=mean_FDImeps_ctx_prevresult,
        xdata='context',         # Column for x-axis (context)
        ydata='relMean_MEPpp_FDI',      # Column for y-axis (mean values)
        huedata='last_was_error',# Column for hue (error status)
        xlabel='Contexts',
        ylabel='Relative FDI MEP Amplitude',     # Label for y-axis
        title='Mean MEPs by Contexts and Previous Result',
        legend_title='Previous Error'
    )
    
    ###### MEP differences Context and Previous Result Analysis 

    # Create a pivot table to calculate mean relMean_MEPpp_FDI for each combination
    pivot_table = pd.pivot_table(mean_FDImeps_ctx_prevresult,
                                values='relMean_MEPpp_FDI',
                                index=['ID_info', 'context'],
                                columns='last_was_error',
                                aggfunc='mean',
                                fill_value=0)

    # Calculate the difference between last_was_error categories
    pivot_table['mean_difference'] = pivot_table[1] - pivot_table[0]
    
    # Back to stack structure
    stacked_df = pivot_table[['mean_difference']].reset_index()
    
    # Plot Difference between previous error and success on MEPs by contexts 
    plot_data.boxplotDot_dataframe_onecategory(
        df=stacked_df,
        x= 'context',
        y= 'mean_difference',
        xlabel='Contexts',         
        ylabel='MEP error - MEP success',     
        title='Relative MEP Mean Difference between Previous Error and Success'
    )