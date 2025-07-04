"""
============================================
Utils

Helper functions or utility functions that assist other modules
    Functions that convert marker names to IDs or vice versa.
    Functions that validate or preprocess marker data.
    Functions that handle file I/O specifically for marker data.

============================================
"""

import mne
import numpy as np

def marker_verification (raw, filtered):
    len_markers_raw = (len(raw.annotations))
    len_markers_filtered = (len(filtered.annotations))
    
    if len_markers_raw == len_markers_filtered:
        print("There are the same amount of markers in raw and filtered data. They are: ")
    else:
        print("There are different amount of markers in raw and filtered data. They are: ")
        
    list_markers_raw = set(raw.annotations.description)
    list_markers_filtered = set(filtered.annotations.description)
    
    print(list_markers_raw)
    print(list_markers_filtered)
        
def add_annotations_to_filtered(raw_filtered, raw_notch):
    """Add annotations from the original raw object to the filtered object."""
    raw_filtered.set_annotations(raw_notch.annotations)
    return raw_filtered

# def extract_events_from_annotations(data_filtered, regexp):
#     """Extracts events from annotations based on a regular expression."""
#     return mne.events_from_annotations(data_filtered, regexp=regexp)

def extract_events_from_annot(events_from_annot, event_ID):
    """Extracts events from annotations based on a regular expression."""
    # Count how many rows will meet the condition to initialize the filtered array
    event_ID_rows = np.sum(events_from_annot[:, 2] == event_ID)
    
    # Initialize a 2D array for the results
    events = np.zeros((event_ID_rows, 2), dtype=int)  # 2 columns for the first and third values
    
    # Index to keep track of the filtered array position
    index = 0

    for row in events_from_annot:
        if row[2] == event_ID:
            # Store the values from the first and third columns in the 2D array
            events[index] = [int(row[0]), int(row[2])]
            index += 1  # Move to the next position in the filtered array
    
    return events

# def create_block_info(play_info_length, n_blocks=6):
#     # Example length of play_info
#     """
#     Create an array of block ids based on the length of play_info.

#     The output array will have the same length as play_info, and will
#     contain a sequence of integers from 1 to 6, where each value is
#     repeated until the length of play_info is reached.

#     Parameters
#     ----------
#     play_info_length : int
#         The length of the play_info array.

#     Returns
#     -------
#     block_id : ndarray
#         An array of block ids.
#     """
#     # Calculate the minimum number of repetitions for each value
#     repeats_per_value = -(-play_info_length // n_blocks)

#     # Create the block_id array with consecutive blocks of values
#     block_id = np.repeat(np.arange(1, n_blocks + 1), repeats_per_value)

#     # Trim the array to match the exact length of play_info
#     block_id = block_id[:play_info_length]
    
#     return block_id

# def create_patterned_array(input_length, fixed_count=200, values=[2, 3, 4, 5, 6]):
#     """
#     Create an array based on the input length where:
#     - Extra slots are filled with 1's.
#     - Fixed counts are assigned to subsequent values.

#     Parameters:
#     - input_length (int): Length of the resulting array.
#     - fixed_count (int): Number of occurrences for each value in `values`.
#     - values (list): Values to fill after the 1's.

#     Returns:
#     - np.ndarray: The generated array.
#     """
#     # Calculate the number of 1's
#     num_ones = input_length - (len(values) * fixed_count)

#     # Create the arrays for 1's and the fixed values
#     ones = np.full(num_ones, 1)
#     others = np.concatenate([np.full(fixed_count, val) for val in values])

#     # Combine the arrays
#     result = np.concatenate([ones, others])

#     return result


def combine_gkg_events(events_from_annot_G2, events_from_annot_G4, events_from_annot_G8):
    """
    Combine Gkg events from different annotations.
    
    Parameters:
    events_from_annot_G2 (numpy array): Events from annotation G2
    events_from_annot_G4 (numpy array): Events from annotation G4
    events_from_annot_G8 (numpy array): Events from annotation G8
    
    Returns:
    events_Gkg (numpy array): Combined Gkg events
    """
    events_Gkg = np.concatenate([
        np.column_stack((events_from_annot_G2[:, 0], np.full(events_from_annot_G2.shape[0], 'Gkg/G  2'))),
        np.column_stack((events_from_annot_G4[:, 0], np.full(events_from_annot_G4.shape[0], 'Gkg/G  4'))),
        np.column_stack((events_from_annot_G8[:, 0], np.full(events_from_annot_G8.shape[0], 'Gkg/G  8')))
    ], axis=0)
    events_Gkg = events_Gkg[np.argsort(events_Gkg[:, 0].astype(int))]  # Sort by event time
    return events_Gkg
      
def convert_to_alfabet(Gx, alfabet):
    """Convert code names to alfabet numbers."""
    return [alfabet.get(i, None) for i in Gx]

# def get_variables_blocks_2_4_6(response_times, choice, sequence, result, elapsed_time, id_block):
#     rs_block_2_4_6 = []
#     cs_block_2_4_6 = []
#     ss_block_2_4_6 = []
#     results_block_2_4_6 = []
#     elapsed_time_block_2_4_6 = []
#     id_block_2_4_6 = []
    
#     for i, j, k, l, m, o in zip(response_times, choice, sequence, result, elapsed_time, id_block):
#         if o == 2 or o == 4 or o == 6:
#             rs_block_2_4_6.append(i)
#             cs_block_2_4_6.append(j)
#             ss_block_2_4_6.append(k)
#             results_block_2_4_6.append(l)
#             elapsed_time_block_2_4_6.append(m)
#             id_block_2_4_6.append(o)
            
#     return rs_block_2_4_6, cs_block_2_4_6, ss_block_2_4_6, results_block_2_4_6, elapsed_time_block_2_4_6, id_block_2_4_6
 
def fill_missing_with_symbolic_value(data_dict, symbolic_value=99999):
    """
    Fills missing values in NumPy arrays within a dictionary with a symbolic value.

    Parameters:
    - data_dict: dict
        A dictionary containing NumPy arrays and/or other data types.
    - symbolic_value: int or float, optional
        The value to replace missing values with (default is 10000).

    Returns:
    - dict: Updated dictionary with missing values filled.
    """
    for key, value in data_dict.items():
        # Check if the value is a NumPy array
        if isinstance(value, np.ndarray):
            data_dict[key] = np.nan_to_num(value, nan=symbolic_value)
    return data_dict

# Define a function to categorize block_info
def categorize_tms_pulse(block):
    if block in [2, 4, 6]:
        return 'Pulse'
    elif block in [1, 3, 5]:
        return 'noPulse'
    else:
        return None  # or any default value if needed

# Using
def count_nan_by_id(df, id_column, columns_to_check):
    """
    Counts the number of NaN values in specified columns for each unique value in an ID column.

    Args:
        df (pd.DataFrame): The input DataFrame.
        id_column (str): The name of the column containing the unique IDs.
        columns_to_check (list): A list of column names to check for NaN values.

    Returns:
        pd.DataFrame: A DataFrame with the counts of NaN values for each ID in the specified columns.
    """

    # Group by the ID column and count NaN values in specified columns
    nan_counts = df.groupby(id_column)[columns_to_check].apply(lambda x: x.isna().sum())

    # Reset the index to make the ID column a regular column
    nan_counts = nan_counts.reset_index()

    return nan_counts
