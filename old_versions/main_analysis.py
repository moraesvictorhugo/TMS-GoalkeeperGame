"""
=================================================
Main Analysis Script
=================================================
"""
from modules import analysis
from modules import import_signal
from modules import plot_data
from modules import utils
from modules import export_data
import numpy as np
import pandas as pd
import locale
import matplotlib.pyplot as plt

# """
# ============================================
# STEP 0 - Importing Data and Setting Flags
# ============================================
# """
## Importing processed csv file
file_path = "/home/victormoraes/MEGA/Archive/IBCCF/Projeto Doc/EMT no Jogo do goleiro/Data processing/TMS-GKg_Analysis/data_TMS-GKg/Processed_data/2025-02-17/"
file_name = "df_gklab.csv"
df = import_signal.import_csv_data(file_path, file_name)

## Setting flags and filtering data
type_analysis = 'group'                  # "individual" or "group"
volunteer_id = 1                          # adjust according to the volunteer number
remove_familiarization_trials = True      # Remove familiarization trials
lst_excluded_volunteers = []
change_location_br = True

if change_location_br:
    # Set locale to use comma as decimal separator (e.g., Brazilian locale)
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

    # Enable locale formatting for Matplotlib
    plt.rcParams['axes.formatter.use_locale'] = True

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
df = analysis.create_last_error(df)

# Create a new column of contexts
df = analysis.create_context_column(df)

# Reorganize data frame
new_order = ['group_info', 'day_info', 'play_info', 'step_info', 'tree_info',
       'ID_info', 'response_time_info', 'response_info',
       'stochastic_chain_info', 'result', 'last_was_error', 'context', 
       'block_info', 'tms_pulse','MEPpp_FDI_µV', 'MEPpp_FDS_µV',
       'relRest_MEPpp_FDI', 'relRest_MEPpp_FDS', 'relMean_MEPpp_FDI',
       'relMean_MEPpp_FDS', 'FDImep_outGame', 'FDSmep_outGame']

# Data frame to start analysis
df = df[new_order]

# Count excluded trials for each volunteer
excluded_trials_volunteers = utils.count_nan_by_id(df, 'ID_info', ['response_time_info', 'relMean_MEPpp_FDI', 'relMean_MEPpp_FDS'])

# Export data frame as csv
export_data.export_to_csv(df, 'df_gklab_analysis.csv')

# """
# ============================================
# STEP 1 - Group Success Rate Analysis
# ============================================
# """

############################################# Global success rate analysis

global_success_rate, std_global_success_rate = analysis.calculate_global_success_rate_group(df)
global_success_rate_with_exclusion, std_global_success_rate_with_exclusion = analysis.calculate_global_success_rate_with_exclusion_group(df,exclude_first_last=100)

# Define labels and plot
global_success_rate_labels = ['Global Success Rate', 'Global Success Rate with 200 trials exclusion']
plot_data.plot_success_rate_comparison_group(global_success_rate, global_success_rate_with_exclusion ,global_success_rate_labels)                            

############################################# Block success rate analysis

# Calculating mean values of individuals and plot
success_rate_blocks = analysis.calculate_success_rate_by_block_group(df)
plot_data.plot_success_rates_by_blocks_group(df)

# Calculating mean values of individuals with and without TMS and plot
success_rate_mean_NoPulse_Pulse_group = analysis.calculate_means_PulseNopulse(success_rate_blocks)
plot_data.plot_means_boxplot(success_rate_mean_NoPulse_Pulse_group)

# """
# ============================================
# STEP 2 - Group Response Times Analysis
# ============================================
# """
############################################# Response Times by Responses

# Calculate mean response times grouped by ID_info and response_info and plot RTs by Responses
mean_response_times_by_responses = df.groupby(['ID_info', 'response_info'])['response_time_info'].mean().reset_index()

plot_data.boxplotDot_dataframe_onecategory(
    df=mean_response_times_by_responses,
    x= 'response_info',
    y= 'response_time_info',
    xlabel='Response',         
    ylabel='Response Times (s)',     
    title='Mean RTs by Responses'
)

############################################# Response Times by Blocks

# Calculate mean response times grouped by ID_info and block_info and plot RTs by Blocks
mean_response_times_by_blocks = df.groupby(['ID_info', 'block_info'])['response_time_info'].mean().reset_index()

plot_data.boxplotDot_dataframe_onecategory(
    df=mean_response_times_by_blocks,
    x= 'block_info',
    y= 'response_time_info',
    xlabel='Block',         
    ylabel='Response Times (s)',     
    title='Mean Response Times by Blocks'
)

############################################# Response Times With TMS and Without TMS

# Calculate mean response times grouped by ID_info and TMS pulse
mean_response_times_NoPulse_Pulse = df.groupby(['ID_info', 'tms_pulse'])['response_time_info'].mean().reset_index()

plot_data.boxplotDot_dataframe_onecategory(
    df=mean_response_times_NoPulse_Pulse,
    x= 'tms_pulse',
    y= 'response_time_info',
    xlabel='',         
    ylabel='Response Times (s)',     
    title='Mean RTs with and without TMS',
    figsize=(10, 6)
)

############################################# Response Times by Contexts

# Get Mean Response Times by Contexts and Plot   
mean_response_times_ctx = df.groupby(['ID_info', 'context'])['response_time_info'].mean().reset_index()

plot_data.boxplotDot_dataframe_onecategory(
    df=mean_response_times_ctx,
    x= 'context',
    y= 'response_time_info',
    xlabel='Contexts',         
    ylabel='Response Times (s)',     
    title='Mean RTs by Contexts'
)

############################################# Plot RTs with EMT by Context    

# Filter RTs during pulses
rt_pulse_df = df.loc[(df['tms_pulse'] == 'Pulse')]

# Get Mean Response Times by Contexts and Plot   
mean_response_times_pulse_ctx = rt_pulse_df.groupby(['ID_info', 'context'])['response_time_info'].mean().reset_index()

plot_data.boxplotDot_dataframe_onecategory(
    df=mean_response_times_pulse_ctx,
    x= 'context',
    y= 'response_time_info',
    xlabel='Contexts',         
    ylabel='Response Times (s)',     
    title='Mean RTs with TMS by Contexts'
)

############################################# Plot RTs without EMT by Context

# FIlter RTs without pulses
rt_nopulse_df = df.loc[(df['tms_pulse'] == 'noPulse')]

# Get Mean Response Times by Contexts and Plot   
mean_response_times_nopulse_ctx = rt_nopulse_df.groupby(['ID_info', 'context'])['response_time_info'].mean().reset_index()

plot_data.boxplotDot_dataframe_onecategory(
    df=mean_response_times_nopulse_ctx,
    x= 'context',
    y= 'response_time_info',
    xlabel='Contexts',         
    ylabel='Response Times (s)',     
    title='Mean RTs without TMS by Contexts'
)

############################################# Plot RTs by Context and Previous result

# Get Mean Response Times by Contexts and Plot   
mean_response_times_ctx_prevresult = df.groupby(['ID_info', 'context', 'last_was_error'])['response_time_info'].mean().reset_index()

# plot_data.boxplot_dataframe_twocategories(
#     df=mean_response_times_ctx_prevresult,
#     xdata='context',         # Column for x-axis (context)
#     ydata='response_time_info',      # Column for y-axis (mean values)
#     huedata='last_was_error',# Column for hue (error status)
#     xlabel='Contexts',
#     ylabel='Response Times (s)',     # Label for y-axis
#     title='Mean RTs by Contexts and Previous Result',
#     legend_title='Previous Error'
# )

############################################# RTs differences by Context and Previous Result Analysis 

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
plot_data.boxplotDotandDash_dataframe_onecategory(
    df=stacked_df,
    x= 'context',
    y= 'mean_difference',
    xlabel='Contexts',         
    ylabel='RT error - RT success',     
    title='RTs Mean Difference between Previous Error and Success'
)

############################################# Plot RTs with TMS by Context and Previous result    

# Filter RTs during pulses
rt_pulse_df = df.loc[(df['tms_pulse'] == 'Pulse')]

# Get Mean Response Times by Contexts and Plot   
mean_response_times_pulse_ctx_prevresult = rt_pulse_df.groupby(['ID_info', 'context', 'last_was_error'])['response_time_info'].mean().reset_index()

# plot_data.boxplot_dataframe_twocategories(
#     df=mean_response_times_pulse_ctx_prevresult,
#     xdata= 'context',
#     ydata= 'response_time_info',
#     huedata='last_was_error',
#     xlabel='Contexts',         
#     ylabel='Response Times (s)',     
#     title='Mean RTs with TMS by Contexts and Previous Result',
#     legend_title='Previous Error'
# )

############################################# RTs differences with TMS by Context and Previous Result Analysis 

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
plot_data.boxplotDotandDash_dataframe_onecategory(
    df=stacked_df,
    x= 'context',
    y= 'mean_difference',
    xlabel='Contexts',         
    ylabel='RT error - RT success',     
    title='RTs Mean Difference with TMS between Previous Error and Success'
)

plot_data.boxplotDotandDashlinezero_dataframe_onecategory(
    df=stacked_df,
    x= 'context',
    y= 'mean_difference',
    subject_id= 'ID_info',
    xlabel='Contexts',         
    ylabel='RT error - RT success',     
    title='RTs Mean Difference with TMS between Previous Error and Success'
)

############################################# Plot RTs without EMT by Context and Previous result

# Filter RTs without pulses
rt_nopulse_df = df.loc[(df['tms_pulse'] == 'noPulse')]

# Get Mean Response Times by Contexts and Plot   
mean_response_times_nopulse_ctx_prevresult = rt_nopulse_df.groupby(['ID_info', 'context', 'last_was_error'])['response_time_info'].mean().reset_index()

# plot_data.boxplot_dataframe_twocategories(
#     df=mean_response_times_nopulse_ctx_prevresult,
#     xdata= 'context',
#     ydata= 'response_time_info',
#     huedata='last_was_error',
#     xlabel='Contexts',         
#     ylabel='Response Times (s)',     
#     title='Mean RTs without TMS by Contexts and Previous Result',
#     legend_title='Previous Error'
# )

############################################# RTs differences without TMS by Context and Previous Result Analysis 

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
plot_data.boxplotDotandDash_dataframe_onecategory(
    df=stacked_df,
    x= 'context',
    y= 'mean_difference',
    xlabel='Contexts',         
    ylabel='RT error - RT success',     
    title='RTs Mean Difference without TMS between Previous Error and Success'
)

plot_data.boxplotDotandDashlinezero_dataframe_onecategory(
    df=stacked_df,
    x= 'context',
    y= 'mean_difference',
    subject_id= 'ID_info',
    xlabel='Contexts',         
    ylabel='RT error - RT success',     
    title='RTs Mean Difference without TMS between Previous Error and Success'
)
     
# """
# ============================================
# STEP 3 - Group MEP Analysis
# ============================================
# """
# Filter MEPs during pulses
meps_blocks_df = df.loc[(df['tms_pulse'] == 'Pulse')]

############################################# MEPs by Blocks

# Calculate mean FDI MEPs grouped by ID_info and block_info
mean_FDImeps_by_blocks = meps_blocks_df.groupby(['ID_info', 'block_info'])['relMean_MEPpp_FDI'].mean().reset_index()

plot_data.boxplotDot_dataframe_onecategory(
    df=mean_FDImeps_by_blocks,
    x= 'block_info',
    y= 'relMean_MEPpp_FDI',
    xlabel='Block',         
    ylabel='Relative FDI MEPs',     
    title='MEP amplitudes by Blocks'
)

############################################# MEPs by Contexts

# Get Mean FDI MEPs relative to mean by Contexts and Plot    
mean_relmFDImepsmean_ctx = meps_blocks_df.groupby(['ID_info', 'context'])['relMean_MEPpp_FDI'].mean().reset_index()

plot_data.boxplotDot_dataframe_onecategory(
    df=mean_relmFDImepsmean_ctx,
    x= 'context',
    y= 'relMean_MEPpp_FDI',
    xlabel='Contexts',         
    ylabel='Relative FDI MEP Amplitude',     
    title='Mean relative MEPs (by mean) by Contexts'
)

plot_data.boxplotDotandDashline_dataframe_onecategory(
    df=mean_relmFDImepsmean_ctx,
    x= 'context',
    y= 'relMean_MEPpp_FDI',
    subject_id= 'ID_info',
    xlabel='Contexts',         
    ylabel='Relative FDI MEP Amplitude',     
    title='Mean relative MEPs (by mean) by Contexts'
)

############################################# MEPs by Context and Previous Result Analysis

# Get Mean FDI MEPs by Contexts and Previous Result and Plot    
mean_FDImeps_ctx_prevresult = meps_blocks_df.groupby(['ID_info', 'context', 'last_was_error'])['relMean_MEPpp_FDI'].mean().reset_index()

# plot_data.boxplot_dataframe_twocategories(
#     df=mean_FDImeps_ctx_prevresult,
#     xdata='context',        
#     ydata='relMean_MEPpp_FDI',      
#     huedata='last_was_error',
#     xlabel='Contexts',
#     ylabel='Relative FDI MEP Amplitude',     
#     title='Mean MEPs by Contexts and Previous Result',
#     legend_title='Previous Error'
# )

############################################# MEP differences Context and Previous Result Analysis 

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
plot_data.boxplotDotandDash_dataframe_onecategory(
    df=stacked_df,
    x= 'context',
    y= 'mean_difference',
    xlabel='Contexts',         
    ylabel='FDI MEP error - MEP success',     
    title='Relative MEP Mean Difference between Previous Error and Success'
)

plot_data.boxplotDotandDashlinezero_dataframe_onecategory(
    df=stacked_df,
    x= 'context',
    y= 'mean_difference',
    subject_id= 'ID_info',
    xlabel='Contexts',         
    ylabel='FDI MEP error - MEP success',     
    title='Relative MEP Mean Difference between Previous Error and Success'
)