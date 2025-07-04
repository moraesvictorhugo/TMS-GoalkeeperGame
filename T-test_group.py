"""
=================================================
Importing modules and data
=================================================
"""
from modules import import_signal
import pandas as pd
import pingouin as pg

# Importing processed csv file
file_path = "/home/victormoraes/MEGA/Archive/IBCCF/Projeto Doc/EMT no Jogo do goleiro/Data processing/TMS-GKg_Analysis/"
file_name = "df_gklab_analysis.csv"
df = import_signal.import_csv_data(file_path, file_name)

"""
=================================================
T-test for each volunteer
=================================================
"""
# Initialize a dictionary to store T-test results
ttest_results_dict = {}

# Loop through each unique volunteer ID
for volunteer_id in df['ID_info'].unique():
    # Filter data for the specific volunteer
    ctx_2_df = df.loc[(df['tms_pulse'] == 'Pulse') & (df['context'] == 2) & (df['ID_info'] == volunteer_id)]
    ctx_10_df = df.loc[(df['tms_pulse'] == 'Pulse') & (df['context'] == 10) & (df['ID_info'] == volunteer_id)]

    # Convert to numpy arrays for T-test
    array_ctx_2 = ctx_2_df['MEPpp_FDI_µV'].to_numpy()
    array_ctx_10 = ctx_10_df['MEPpp_FDI_µV'].to_numpy()

    # # Perform T-test only if both arrays have data    
    # ttest_results = pg.ttest(array_ctx_2, array_ctx_10, paired=False, alternative='two-sided', confidence=0.95)
    # ttest_results_dict[volunteer_id] = ttest_results

    # Perform Man-Whitney U test
    ttest_results = pg.mwu(array_ctx_2, array_ctx_10, alternative='two-sided')
    ttest_results_dict[volunteer_id] = ttest_results

# # Optionally convert results to a DataFrame for better readability
ttest_results_df = pd.concat(ttest_results_dict).reset_index()

