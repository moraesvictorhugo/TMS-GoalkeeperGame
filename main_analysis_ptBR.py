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
file_path = '/home/victormoraes/MEGA/Archive/PhD IBCCF-UFRJ/PhD/EMT no Jogo do goleiro/Data processing/data_TMS-GKg/Processed_data/2025-08-27'
file_name = "df_all_data_processed.csv"
df = import_signal.import_csv_data(file_path, file_name)

## Setting flags and filtering data
type_analysis = 'group'                  # "individual" or "group"
volunteer_id = 1                          # adjust according to the volunteer number
remove_familiarization_trials = True      # Remove familiarization trials
lst_excluded_volunteers = []
change_location_br = False
remove_block = []                         # Remove undesired block for analysis

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

# Remove block
if remove_block:
    df = df[~df['block_info'].isin(remove_block)]

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
excluded_trials_volunteers = utils.count_nan_by_id(df, 'ID_info', ['response_time_info', 'relMean_MEPpp_FDI'])

# Export data frame as csv
export_data.export_to_csv(df, 'df_gklab_analysis_20250611.csv')

# """
# ============================================
# STEP 1 - Group Success Rate Analysis
# ============================================
# """

############################################# Global success rate analysis

global_success_rate, std_global_success_rate = analysis.calculate_global_success_rate_group(df)
global_success_rate_with_exclusion, std_global_success_rate_with_exclusion = analysis.calculate_global_success_rate_with_exclusion_group(df,exclude_first_last=100)

# Define labels and plot
global_success_rate_labels = ['1200 tentativas', '1000 tentativas']
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
    xlabel='Resposta',         
    ylabel='Tempo de resposta (seg)',     
    title=' ',
    figsize=(10, 6)
)

############################################# Response Times by Blocks

# Calculate mean response times grouped by ID_info and block_info and plot RTs by Blocks
mean_response_times_by_blocks = df.groupby(['ID_info', 'block_info'])['response_time_info'].mean().reset_index()

plot_data.boxplotDot_dataframe_onecategory(
    df=mean_response_times_by_blocks,
    x= 'block_info',
    y= 'response_time_info',
    xlabel='Bloco',         
    ylabel='Tempo de resposta (seg)',     
    title=' ',
    figsize=(10, 6),
    ylim=(0.2, 1)
)

############################################# Response Times With TMS and Without TMS

# Calculate mean response times grouped by ID_info and TMS pulse
mean_response_times_NoPulse_Pulse = df.groupby(['ID_info', 'tms_pulse'])['response_time_info'].mean().reset_index()

plot_data.boxplotDot_dataframe_onecategory(
    df=mean_response_times_NoPulse_Pulse,
    x= 'tms_pulse',
    y= 'response_time_info',
    xlabel='',         
    ylabel='Tempo de resposta (seg)',     
    title=' ',
    figsize=(10, 6)
)

############################################# Response Times by Contexts

# Get Mean Response Times by Contexts and Plot   
mean_response_times_ctx = df.groupby(['ID_info', 'context'])['response_time_info'].mean().reset_index()

plot_data.boxplotDot_dataframe_onecategory(
    df=mean_response_times_ctx,
    x= 'context',
    y= 'response_time_info',
    xlabel='Contexto',         
    ylabel='Tempo de resposta (seg)',     
    title=' ',
    figsize=(10, 6)
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
    xlabel='Context',         
    ylabel='Response Times (sec)',     
    title='RTs with EMT by Context',
    figsize=(10, 6),
    ylim=(0.25, 0.75)
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
    xlabel='Contexto',         
    ylabel='Tempo de resposta (seg)',     
    title='TR sem EMT',
    figsize=(10, 6)
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
    xlabel='Contexto',         
    ylabel='TR erro − TR acerto',     
    title=' ',
    figsize=(10, 6)
)

plot_data.boxplotDotandDashlinezero_dataframe_onecategory(
    df=stacked_df,
    x= 'context',
    y= 'mean_difference',
    subject_id= 'ID_info',
    xlabel='Contexto',         
    ylabel='TR erro − TR acerto',     
    title='TRs após erro − TRs após sucesso com 1200 jogadas',
    figsize=(10, 6)
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
    xlabel='Contexto',         
    ylabel='TR erro − TR acerto',     
    title='TRs após erro − TRs após sucesso com EMT',
    figsize=(10, 6)
)

plot_data.boxplotDotandDashlinezero_dataframe_onecategory(
    df=stacked_df,
    x= 'context',
    y= 'mean_difference',
    subject_id= 'ID_info',
    xlabel='Context',         
    ylabel='RT after error − after success',     
    title='TRs após erro − TRs após sucesso com EMT',
    figsize=(10, 6),
    ylim=(-0.3, 0.2)
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
    xlabel='Contexto',         
    ylabel='TR erro − TR acerto',     
    title='TRs após erro − TRs após sucesso sem EMT',
    figsize=(10, 6)
)

plot_data.boxplotDotandDashlinezero_dataframe_onecategory(
    df=stacked_df,
    x= 'context',
    y= 'mean_difference',
    subject_id= 'ID_info',
    xlabel='Contexto',         
    ylabel='TR erro − TR acerto',     
    title='TRs após erro − TRs após sucesso sem EMT',
    figsize=(10, 6)
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
    xlabel='Bloco',         
    ylabel='PEMs relativos no PID',     
    title=' ',
    figsize=(10, 6)
)

############################################# MEPs by Contexts - FDI

# Get Mean FDI MEPs relative to mean by Contexts and Plot    
mean_relmFDImepsmean_ctx = meps_blocks_df.groupby(['ID_info', 'context'])['relMean_MEPpp_FDI'].mean().reset_index()

plot_data.boxplotDot_dataframe_onecategory(
    df=mean_relmFDImepsmean_ctx,
    x= 'context',
    y= 'relMean_MEPpp_FDI',
    xlabel='Context',         
    ylabel='FDI relative MEPs',     
    title=' ',
    figsize=(10, 6)
)

plot_data.boxplotDotandDashline_dataframe_onecategory(
    df=mean_relmFDImepsmean_ctx,
    x= 'context',
    y= 'relMean_MEPpp_FDI',
    subject_id= 'ID_info',
    xlabel='Contexto',         
    ylabel='PEMs relativos no PID',     
    title=' ',
    figsize=(10, 6),
    ylim=(0.90, 1.20)
)

############################################# MEPs by Contexts - FDS

# Get Mean FDS MEPs relative to mean by Contexts and Plot    
mean_relmFDSmepsmean_ctx = meps_blocks_df.groupby(['ID_info', 'context'])['relMean_MEPpp_FDS'].mean().reset_index()

plot_data.boxplotDot_dataframe_onecategory(
    df=mean_relmFDSmepsmean_ctx,
    x= 'context',
    y= 'relMean_MEPpp_FDS',
    xlabel='Context',         
    ylabel='FDS relative MEPs',     
    title=' ',
    figsize=(10, 6)
)

plot_data.boxplotDotandDashline_dataframe_onecategory(
    df=mean_relmFDSmepsmean_ctx,
    x= 'context',
    y= 'relMean_MEPpp_FDS',
    subject_id= 'ID_info',
    xlabel='Contexto',         
    ylabel='PEMs relativos no FSD',     
    title=' ',
    figsize=(10, 6),
    ylim=(0.90, 1.20)
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
    xlabel='Contexto',         
    ylabel='PEMs relativos no PID após erro − após sucesso',     
    title=' ',
    figsize=(10, 6)
)

plot_data.boxplotDotandDashlinezero_dataframe_onecategory(
    df=stacked_df,
    x= 'context',
    y= 'mean_difference',
    subject_id= 'ID_info',
    xlabel='Context',         
    ylabel='FDI relative MEPs after error − after success',     
    title=' ',
    figsize=(10, 6)
)

### Create the plot to view just MEP differences between previous error and success in contexts 10 and 2 -------------- - CRIAR FUNÇÂO!!!!
filt_ctx_10and2_MEPdiff = stacked_df.loc[stacked_df['context'].isin(['10', '2'])]

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Create a boxplot
plt.figure(figsize=(10, 6), dpi=600)

# Boxplot without hue to avoid the warning
sns.boxplot(x='context', y='mean_difference', data=filt_ctx_10and2_MEPdiff, color='lightgray', showfliers=False)

# Scatterplot for individual data points
sns.stripplot(x='context', y='mean_difference', data=filt_ctx_10and2_MEPdiff, color='black', jitter=False, alpha=0.7)

# Add lines linking data points based on ID_info
for id_value in filt_ctx_10and2_MEPdiff['ID_info'].unique():
    subset = filt_ctx_10and2_MEPdiff[filt_ctx_10and2_MEPdiff['ID_info'] == id_value]
    if id_value in [2, 3, 5, 8, 10]:  # Blue lines for these IDs
        color = 'blue'
    elif id_value in [4, 6, 9]:       # Green lines for these IDs
        color = 'green'
    else:
        color = 'gray'
    plt.plot(subset['context'], subset['mean_difference'], color=color, linewidth=1.5, alpha=0.7)

# Add title and labels
# plt.title('Boxplot of Mean Difference by Context with Linked Data Points')
plt.xlabel('Contexto')
plt.ylabel('PEMs relativos no PID após erro − após sucesso')

# Remove spines
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)

# Add line at y=0
plt.axhline(y=0, color='gray', linestyle='--', linewidth=1)

# Show plot
plt.show()
