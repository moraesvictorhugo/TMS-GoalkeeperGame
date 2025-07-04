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

"""
============================================
STEP 0 - Importing Data and Setting Flags
============================================
"""
## Importing processed csv file
file_path = "/home/victormoraes/MEGA/Archive/IBCCF/Projeto Doc/EMT no Jogo do goleiro/Data processing/TMS-GKg_Analysis/data_TMS-GKg/Processed_data/"
file_name = "df_gklab.csv"
df = import_signal.import_csv_data(file_path, file_name)

## Setting flags and filtering data
type_analysis = 'group'                  # "individual" or "group"
volunteer_id = 4                          # adjust according to the volunteer number
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

"""
============================================
STEP 1 - Individual Success Rate Analysis
============================================
"""
# if type_analysis == 'individual':
#     # Global success rate analysis
#     global_success_rate, _ = analysis.calculate_global_success_rate_individual(df)
#     global_success_rate_with_exclusion, _ = analysis.calculate_global_success_rate_with_exclusion_individual(df, exclude_first_last=100)

#     # Define Plot parameters
#     global_success_rates = [global_success_rate, global_success_rate_with_exclusion]
#     global_success_rate_labels = ['Global Success Rate', 'Global Success Rate with Exclusion']
#     global_success_rate_colors = ['cornflowerblue', 'limegreen']

#     # Call the function
#     plot_data.plot_success_rate_individual(global_success_rates, global_success_rate_labels, global_success_rate_colors)

#     # Block success rate analysis
#     success_rate_block1, success_rate_block2, success_rate_block3, success_rate_block4, success_rate_block5, success_rate_block6 = analysis.calculate_success_rate_by_block_individual(df)

#     # Define Plot parameters
#     block_success_rates = [success_rate_block1, success_rate_block2, success_rate_block3, success_rate_block4, success_rate_block5, success_rate_block6]
#     block_success_rate_labels = ['Block 1', 'Block 2', 'Block 3', 'Block 4', 'Block 5', 'Block 6']

#     # Call the function
#     plot_data.plot_success_rate_individual(block_success_rates, block_success_rate_labels) #, block_success_rate_colors)

#     # Sucess rate with and without TMS
#     success_rate_with_tms = np.mean([success_rate_block2, success_rate_block4, success_rate_block6])
#     success_rate_without_tms = np.mean([success_rate_block1, success_rate_block3, success_rate_block5])

#     # Define Plot parameters
#     success_rates = [success_rate_with_tms, success_rate_without_tms]
#     success_rate_labels = ['With TMS', 'Without TMS']
#     success_rate_colors = ['cornflowerblue', 'limegreen']

#     # Call the function
#     plot_data.plot_success_rate_individual(success_rates, success_rate_labels, success_rate_colors)


# ### Noslem criteria analysis to exclude participants

# # Apply a logit transformation to the data for normalized proportion of correct guesses


# # Split data in windows


# # Fit a Least Squares Regression Model


# # Plot the data


# # Remove negative slopes individuals in step 0


# # ------------------------------------------------------------------------------------

# """
# ============================================
# STEP 1 - Group Success Rate Analysis
# ============================================
# """
if type_analysis == 'group':
    # Global success rate analysis
    global_success_rate, std_global_success_rate = analysis.calculate_global_success_rate_group(df)
    global_success_rate_with_exclusion, std_global_success_rate_with_exclusion = analysis.calculate_global_success_rate_with_exclusion_group(df,exclude_first_last=100)

    # Define Plot parameters
    global_success_rate_labels = ['Global Success Rate', 'Global Success Rate with Exclusion']

    # Call the function
    # plot_data.plot_success_rate_comparison_group(global_success_rate, global_success_rate_with_exclusion ,global_success_rate_labels)                            

    # Block success rate analysis
    success_rate_blocks = analysis.calculate_success_rate_by_block_group(df)
    # plot_data.plot_success_rates_by_blocks_group(df)
    # plot_data.plot_success_rates_by_blocks_stripplot(df)

    # Calculating mean values of individuals with and without TMS
    success_rate_mean_NoPulse_Pulse_group = analysis.calculate_means_PulseNopulse(success_rate_blocks)

    # Plot sucess rate with and without TMS
    plot_data.plot_means_boxplot(success_rate_mean_NoPulse_Pulse_group)

"""
============================================
STEP 2 - Response Times Analysis
============================================
"""

# Calculate mean response times grouped by ID_info and block_info
mean_response_times_by_blocks = df.groupby(['ID_info', 'block_info'])['response_time_info'].mean().reset_index()

# Plot RTs by Block
plot_data.plot_boxplot(mean_response_times_by_blocks, 'response_time_info', 'block_info', title='Mean Response Times by Block', xlabel='Blocks', ylabel='RTs (s)', figsize=(10, 6), dpi=600, outlier_threshold=1.5)


# Calculate mean response times grouped by ID_info and block_info
mean_response_times_NoPulse_Pulse = df.groupby(['ID_info', 'tms_pulse'])['response_time_info'].mean().reset_index()

# Plot RTs by TMS pulse
plot_data.plot_boxplot(mean_response_times_NoPulse_Pulse, 'response_time_info', 'tms_pulse', title='Response Times by TMS Pulse', xlabel='TMS Pulses', ylabel='RTs (s)', figsize=(10, 6), dpi=600, outlier_threshold=1.5)



# # ------------------------------------------------------------------------------------
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

"""
============================================
STEP 3 - MEP Analysis
============================================
"""
# Plot RTs by Block
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

"""
============================================
STEP 6 - Post-Error Analysis
============================================

Processa no MATLAB com a função lastwaserror e importa o CSV com tabela sumarizada para plotar aqui
Esse processo foi feito manualmente. Preciso otimizar essa etapa.

"""
import pandas as pd
from modules import plot_data

# Importing processed csv file
file_path = "/home/victormoraes/MEGA/Archive/IBCCF/Projeto Doc/EMT no Jogo do goleiro/Data processing/TMS-GKg_Analysis/data_TMS-GKg/Processed_data/Final analysis"
file_name = "analysis_FER_V02.csv"

# Reading a CSV file with a semicolon as a separator
df = pd.read_csv(file_path + '/' + file_name, sep=';')

# Filter columns
df = df.iloc[:, :5]

# Convert column ctx to string
df['ctx'] = df['ctx'].astype(str)

# Change 0 in df['ctx'] to '00'
df['ctx'] = df['ctx'].replace('0', '00')

# Filtering data and removing outliers
rt_df = df[df['ctx_rtime'] < 1.5]
rt_pulse_df = df.loc[(df['ctx_rtime'] < 1.5) & (df['condition'] == 'Pulse')]
rt_NoPulse_df = df.loc[(df['ctx_rtime'] < 1.5) & (df['condition'] == 'noPulse')]

mep_df = df[df['ctx_mep'] < 1000]


# Plot RTs by Context and Previous Result
plot_data.boxplot_separated_by_ctx_and_fer(
    rt_df,
    xdata='ctx',
    ydata='ctx_rtime',
    huedata='ctx_fer',
    ylabel='Response Time (s)',
    title='Response Times by Context and Previous Result',
    legend_labels=['No Error', 'Error']
)

# Plot RTs with EMT by Context and Previous Result
plot_data.boxplot_separated_by_ctx_and_fer(
    rt_pulse_df,
    xdata='ctx',
    ydata='ctx_rtime',
    huedata='ctx_fer',
    ylabel='Response Time (s)',
    title='Response Times with TMS by Context and Previous Result',
    legend_labels=['No Error', 'Error']
)

# Plot RTs without EMT by Context and Previous Result
plot_data.boxplot_separated_by_ctx_and_fer(
    rt_NoPulse_df,
    xdata='ctx',
    ydata='ctx_rtime',
    huedata='ctx_fer',
    ylabel='Response Time (s)',
    title='Response Times without TMS by Context and Previous Result',
    legend_labels=['No Error', 'Error']
)

# Plot MEPs by Context and Previous Result
plot_data.boxplot_separated_by_ctx_and_fer(
    mep_df,
    xdata='ctx',
    ydata='ctx_mep',
    huedata='ctx_fer',
    ylabel='Motor Evoked Potential Amplitude (µV)',
    title='MEPs by Context and Previous Result',
    legend_labels=['No Error', 'Error']
)

# Describe RTs by context and previous result
rt_df.groupby(['ctx', 'ctx_fer'])['ctx_rtime'].describe()

# Describe RTs by context and previous result
rt_pulse_df.groupby(['ctx', 'ctx_fer'])['ctx_rtime'].describe()

# Describe RTs by context and previous result
rt_NoPulse_df.groupby(['ctx', 'ctx_fer'])['ctx_rtime'].describe()

# Describe MEPs by context and previous result
mep_df.groupby(['ctx', 'ctx_fer'])['ctx_mep'].describe()

# -------------------------------------------------------------------------

# mep_df.to_csv('mep_df.csv', index=False)