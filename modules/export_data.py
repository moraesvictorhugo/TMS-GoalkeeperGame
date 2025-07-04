"""
=================================================
Export Functions
=================================================
"""
import pandas as pd
import numpy as np


def create_df_from_dict(variables_dict):
    """
    Creates a DataFrame from a dictionary where the keys are column names
    and the values are the data to be included in the DataFrame.

    Parameters:
    - variables_dict: Dictionary containing variable names as keys and data as values.

    Returns:
    - DataFrame constructed from the dictionary.
    """
    return pd.DataFrame({key: (value if isinstance(value, (list, pd.Series, np.ndarray)) else [value])
                         for key, value in variables_dict.items()})

# def create_df_GKlab(df_summary):
#     df_GKlab = pd.DataFrame({
#     'group_info': np.full(len(trial_numbers), 1),
#     'day_info': np.full(len(trial_numbers), 1),
#     'trial': trial_numbers,
#     'step_info': np.full(len(trial_numbers), 1),
#     'tree_info': np.full(len(trial_numbers), 13),
#     'ID_info': np.full(len(trial_numbers), volunteer),
#     'response_time_info': response_times,
#     'response_info': choice,
#     'stochastic_chain_info': sequence,
#     'elapsed_time_info': elapsed_time,
#     'relative_MEPpp_FDI_withExclusions': relative_MEPpp_FDI_withExclusion,
#     'relative_MEPpp_FDS_withExclusions': relative_MEPpp_FDS_withExclusion
# })
#     return df_GKlab

def export_to_csv(data, filename):
    """Exports data to a CSV file."""
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)

def export_to_GKlab_csv(data, filename):
    """Exports data to a CSV file in the GKlab format."""
    df_GKlab = pd.DataFrame(data)
    df_GKlab.to_csv(filename, index=False)

