import pandas as pd
import numpy as np


def calculate_global_success_rate_group(df):
    """
    Calculate the mean and standard deviation of success rates for each group defined by 'ID_info'.

    This function groups the input DataFrame by the 'ID_info' column and computes the mean
    and standard deviation of success rates, defined as the proportion of correct responses
    (where 'response_info' matches 'stochastic_chain_info') for each unique ID.

    Parameters:
    df (pd.DataFrame): A DataFrame containing the following columns:
        - 'ID_info': Identifier for grouping the data.
        - 'response_info': The responses given by participants.
        - 'stochastic_chain_info': The correct responses against which 'response_info' is compared.

    Returns:
    tuple: A tuple containing:
        - means (list): A list of mean success rates for each unique ID in 'ID_info'.
        - stds (list): A list of SD of success rates for each unique ID in 'ID_info'.
    """

    # Group by 'ID_info' and calculate mean and std for each group
    grouped = df.groupby('ID_info').apply(
        lambda group: pd.Series({
            'mean': (group['response_info'] == group['stochastic_chain_info']).mean(),
            'std': (group['response_info'] == group['stochastic_chain_info']).std()
        })
    )

    # Extract results as lists
    means = grouped['mean'].tolist()
    stds = grouped['std'].tolist()

    return means, stds

def calculate_means_PulseNopulse(success_rate_blocks):
    """
    Calculate mean values for each key in a nested dictionary based on specified rules.

    Parameters:
    success_rate_blocks (dict): A nested dictionary where each key has another dictionary of values.

    Returns:
    dict: A new dictionary with keys 'NoPulse' and 'Pulse' for each original key.
    """
    result = {}

    # Iterate through each key in the original dictionary
    for key, inner_dict in success_rate_blocks.items():
        # Extract values for keys 1, 3, 5 and keys 2, 4, 6
        values_NoPulse = [inner_dict.get(i)
                          for i in [1, 3, 5] if i in inner_dict]
        values_Pulse = [inner_dict.get(i)
                        for i in [2, 4, 6] if i in inner_dict]

        # Calculate means if there are values to calculate
        mean_NoPulse = np.mean(values_NoPulse) if values_NoPulse else None
        mean_Pulse = np.mean(values_Pulse) if values_Pulse else None

        # Store results in the new dictionary
        result[key] = {
            'mean_NoPulse': mean_NoPulse,
            'mean_Pulse': mean_Pulse
        }

    return result


def calculate_global_success_rate_with_exclusion_group(df, exclude_first_last=100):
    """
    Calculate the global success rate for each group in ID_info with optional exclusion of rows.

    Parameters:
    df (pd.DataFrame): A DataFrame containing the columns 'ID_info', 'response_info', 'stochastic_chain_info', and 'play_info'.
    exclude_first_last (int): Number of rows to exclude from the beginning and end of each group's data.

    Returns:
    means (list): A list of mean success rates for each ID_info.
    stds (list): A list of standard deviations for each ID_info.
    """

    # Initialize lists to store means and standard deviations
    means = []
    stds = []

    # Group by 'ID_info'
    grouped = df.groupby('ID_info')

    for name, group in grouped:
        # # Exclude the first and last specified number of rows for each group
        group_trimmed = group.iloc[exclude_first_last:-exclude_first_last]

        # Calculate mean and std for the trimmed group
        mean_success_rate = (
            group_trimmed['response_info'] == group_trimmed['stochastic_chain_info']).mean()
        std_success_rate = (
            group_trimmed['response_info'] == group_trimmed['stochastic_chain_info']).std()

        # Append results to lists
        means.append(mean_success_rate)
        stds.append(std_success_rate)

    return means, stds


def calculate_success_rate_by_block_group(df):
    """
    Calculate success rates for each unique block in 'block_info', grouped by 'ID_info'.

    Parameters:
    df (pd.DataFrame): A DataFrame containing 'ID_info', 'block_info', 'response_info', and 'stochastic_chain_info'.

    Returns:
    dict: A dictionary where keys are IDs and values are dictionaries with block numbers as keys and their corresponding success rates as values.
    """
    # Initialize a dictionary to store results
    results = {}

    # Group by 'ID_info'
    for id_value, group in df.groupby('ID_info'):
        # For each ID, calculate success rates for each block
        success_rates = group.groupby('block_info').apply(
            lambda block: (block['response_info'] ==
                           block['stochastic_chain_info']).mean()
        ).to_dict()

        # Store the results in the dictionary
        results[id_value] = success_rates

    return results

# Using
def create_last_error(df):
    """
    This function updates the 'last_was_error' column in the DataFrame based on the
    conditions specified regarding 'stochastic_chain_info' and 'result' columns.
    
    Parameters:
    df (pd.DataFrame): The DataFrame containing the relevant columns.
    
    Returns:
    pd.DataFrame: The updated DataFrame with 'last_was_error' column modified.
    """
    # Reset index
    df = df.reset_index(drop=True)  # Ensure sequential 0-based index
    
    # Initialize 'last_was_error' column with NaN or 0
    df['last_was_error'] = 0
    
    # Iterate through the DataFrame starting from the second row
    for i in range(1, len(df)):
        # Check if the previous row has stochastic_chain_info == 1
        if df.at[i-1, 'stochastic_chain_info'] == 1:
            # Check if the current row's result is correct or incorrect
            if df.at[i, 'result'] == 'correct':
                # Set current row and next two rows to 0 if within bounds
                df.at[i + 1, 'last_was_error'] = 0
                if i + 2 < len(df):
                    df.at[i + 2, 'last_was_error'] = 0
                if i + 3 < len(df):
                    df.at[i + 3, 'last_was_error'] = 0
            elif df.at[i, 'result'] == 'incorrect':
                # Set current row and next two rows to 1 if within bounds
                df.at[i + 1, 'last_was_error'] = 1
                if i + 2 < len(df):
                    df.at[i + 2, 'last_was_error'] = 1
                if i + 3 < len(df):
                    df.at[i + 3, 'last_was_error'] = 1

    return df


def create_context_column(df):
    # Initialize the context column with NaN and set its dtype to object
    df['context'] = np.nan  # Initialize with NaN
    df['context'] = df['context'].astype(object)  # Set dtype to object
    
    # Iterate through the DataFrame
    for i in range(1, len(df)):
        # Check for block change
        if df['block_info'].iloc[i] != df['block_info'].iloc[i - 1]:
            continue  # The first row of a new block remains NaN
        
        # Get the value of stochastic_chain_info from the previous rows
        prev_value = df['stochastic_chain_info'].iloc[i - 1]
        
        if prev_value == 0:
            # If previous value is 0, check further up
            if i > 1:
                prev_value = df['stochastic_chain_info'].iloc[i - 2]
                if prev_value == 0:
                    df.loc[i, 'context'] = '00'  # Use .loc for assignment
                elif prev_value == 1:
                    df.loc[i, 'context'] = '10'  # Use .loc for assignment
                elif prev_value == 2:
                    df.loc[i, 'context'] = '20'  # Use .loc for assignment
        elif prev_value == 1:
            df.loc[i, 'context'] = '1'      # Use .loc for assignment
        elif prev_value == 2:
            df.loc[i, 'context'] = '2'      # Use .loc for assignment
    
    return df









