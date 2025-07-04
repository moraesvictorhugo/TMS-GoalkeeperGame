"""
============================================
Signal Processing

Functions that directly manipulate or analyze the signal based on markers:
    Functions that extract events or markers from the signal.
    Functions that perform calculations or transformations using the markers.
    Functions that plot or visualize the signal with respect to the markers
============================================
"""
import mne
import numpy as np

def downsample_data(raw, new_sfreq=3000):
    """Downsamples raw data to a new sample frequency."""
    raw.resample(new_sfreq)
    return raw

def notch_filter_data(raw, freqs=60):
    """Applies a notch filter to the raw data."""
    return raw.copy().notch_filter(freqs=freqs)

def apply_bandpass_filter(raw, l_freq=20, h_freq=500):
    """Apply Butterworth bandpass filter from l_freq to h_freq."""
    data_filtered = mne.filter.filter_data(raw.get_data(), 
                                           sfreq=raw.info['sfreq'], 
                                           l_freq=l_freq, h_freq=h_freq, 
                                           method='iir', iir_params=dict(order=2, ftype='butter'))
    return data_filtered

def create_filtered_raw_object(data_filtered, raw_info):
    """Create a new Raw object with the filtered data."""
    raw_filtered = mne.io.RawArray(data_filtered, raw_info)
    return raw_filtered

# def split_events_into_blocks(events_from_annotations, event_id, sfreq=3000, block_duration_sec=60, min_block_length=10):
#     """
#     Splits events into blocks based on a specified event ID, including all events within each block, and returns separate arrays for each block.

#     Parameters:
#     - events_from_annotations: Array with three columns, where column 1 is sample index, column 3 is event ID.
#     - event_id: The specific event ID used to define the start of a new block.
#     - sfreq: Sampling frequency in Hz (default is 3000 Hz).
#     - block_duration_sec: Maximum interval in seconds between event IDs to consider as part of the same block.
#     - min_block_length: Minimum number of consecutive event IDs to consider as a valid block.

#     Returns:
#     - Six separate arrays (events_from_annot_B1, ..., events_from_annot_B6) for each block.
#     """
#     block_duration_samples = block_duration_sec * sfreq
#     blocks = [[] for _ in range(6)]
#     current_block = []
#     block_index = 0  # Track the current block

#     for i in range(1, len(events_from_annotations)):
#         sample, _, curr_event_id = events_from_annotations[i]
#         previous_sample = events_from_annotations[i - 1][0]
#         interval = sample - previous_sample

#         # Start or continue the current block
#         if curr_event_id == event_id or (interval <= block_duration_samples and current_block):
#             current_block.append(events_from_annotations[i])

#         # Finalize the block if interval exceeds the threshold
#         if interval > block_duration_samples and current_block:
#             # Only save if block meets the minimum length and we have space
#             if len(current_block) >= min_block_length and block_index < 6:
#                 blocks[block_index] = np.array(current_block)
#                 block_index += 1
#             current_block = []

#     # Handle the final block
#     if len(current_block) >= min_block_length and block_index < 6:
#         blocks[block_index] = np.array(current_block)

#     # Return separate arrays for each block
#     return blocks[0], blocks[1], blocks[2], blocks[3], blocks[4], blocks[5]

# def split_events_into_blocks_manually(data, split_value=10, max_segments=10):
#     """
#     Splits the input ndarray whenever the third column equals a specified value
#     and returns independent arrays for each segment.
    
#     Parameters:
#     - data: ndarray with at least 3 columns.
#     - split_value: Value to split on in the third column (default is 10).
#     - max_segments: Maximum number of segments to return (default is 10).
    
#     Returns:
#     - Independent arrays for each segment, padded with empty arrays if there are fewer than max_segments.
#     """
#     # Ensure the input data has at least 3 columns
#     if data.shape[1] < 3:
#         raise ValueError("Input data must have at least 3 columns.")
    
#     # List to store the segments
#     segments = []
#     current_segment = []  # Temporary list to hold the current segment
    
#     # Iterate through the rows of the ndarray
#     for row in data:
#         if row[2] == split_value:  # Check the third column for the split value
#             if current_segment:  # Only add if there's data above the split value
#                 segments.append(np.array(current_segment))  # Store the current segment
#                 current_segment = []  # Reset for the next segment
#         else:
#             current_segment.append(row)  # Store rows that are not part of a split
    
#     # Add the last segment if there's remaining data
#     if current_segment:
#         segments.append(np.array(current_segment))
    
#     # Pad with empty arrays to ensure exactly max_segments are returned
#     segments += [np.empty((0, data.shape[1]))] * (max_segments - len(segments))
    
#     # Return segments as separate arrays, up to max_segments
#     return segments[:max_segments]


def split_events_InOut_game(events_from_annot):
    # Get the marker column
    """
    Splits the event annotations into two groups based on the occurrence of marker 'D4'.

    This function processes the provided event annotations to identify sequences where 
    the marker 'D4' appears in consecutive events. The events are split into two groups: 
    one containing the rows where the marker 'D4' is found in such sequences, and the 
    other containing the remaining events.

    Parameters:
    events_from_annot (ndarray): A numpy array of event annotations where each row 
                                 contains event data with the marker information in 
                                 the third column.

    Returns:
    tuple: A tuple containing two numpy arrays. The first array consists of rows where 
           the marker 'D4' is in consecutive events, and the second array contains the 
           remaining rows.
    """
    marker_col = events_from_annot[:, 2]

    # Create boolean masks for the conditions
    is_D4 = marker_col == 4
    prev_is_D4 = np.roll(is_D4, 1)  # Check if the previous element is 4
    next_is_D4 = np.roll(is_D4, -1)  # Check if the next element is 4

    # Handle edge cases to prevent wrapping
    prev_is_D4[0] = False
    next_is_D4[-1] = False

    # Combine conditions: current 4 and either previous or next is 4
    condition = is_D4 & (prev_is_D4 | next_is_D4)

    # Split the array into two new variables
    events_from_annot_outGame = events_from_annot[condition]  # Rows that match the condition
    events_from_annot_inGame = events_from_annot[~condition]  # Rows that don't match the condition

    return events_from_annot_outGame, events_from_annot_inGame

def calculate_response_times(events_D2, events_Gkg, data_filtered):
    """Calculates response times and identifies Gx1 and Gx2."""
    response_times = []
    Gx1 = []
    Gx2 = []

    for event_D2 in events_D2[:, 0]:
        future_events = events_Gkg[events_Gkg[:, 0].astype(int) > event_D2]
        if future_events.size > 0:
            next_event_time = int(future_events[0, 0])
            next_event_name = future_events[0, 1]
            response_time = (next_event_time - event_D2) / data_filtered.info['sfreq']
            response_times.append(response_time)
            Gx1.append(next_event_name)

            further_events = future_events[1:]  # Events after the identified Gx1
            if further_events.size > 0:
                next_next_event_name = further_events[0, 1]
                Gx2.append(next_next_event_name)
            else:
                Gx2.append(None)  # No further event found
        else:
            Gx1.append(None)  # No next event found
            Gx2.append(None)  # No further event found

    return response_times, Gx1, Gx2

def analyze_choice(choice, sequence):
    """Analyze the correctness of choices."""
    return ['correct' if i == j else 'incorrect' for i, j in zip(choice, sequence)]

# def calculate_elapsed_time(events_from_annot_D1, data_filtered):
#     """Calculate elapsed time in seconds at each trial marked by D1."""
#     return [i / data_filtered.info['sfreq'] for i in events_from_annot_D1[:, 0]]

def create_trigger_array(data_filtered):
    """Create a trigger array with 12s where the events D4 are identified."""
    events_from_annot_D4, event_dict_D4 = mne.events_from_annotations(data_filtered, regexp="Display/D  4")
    events_D4 = events_from_annot_D4[:, 0]
    trigger = np.zeros(data_filtered.n_times)
    for i in events_D4:
        trigger[i] = 12
    return trigger

# def split_d4_events(events, d4_event_id):
#     """Split D4 events into D4_stim and D4_rest and remove the first 12 D4_stim events."""
#     D4_stim = []
#     D4_rest = []
    
#     for i in range(len(events)):
#         if events[i, 2] == d4_event_id:  # Check if it's a D4 event
#             if i > 0 and events[i - 1, 2] != d4_event_id:                  # Preceded by a non-D4 event
#                 D4_stim.append(events[i, 0])
#             elif i < len(events) - 1 and events[i + 1, 2] != d4_event_id:  # Followed by a non-D4 event
#                 D4_stim.append(events[i, 0])
#             else:                                          # No other event nearby, consider it as rest
#                 D4_rest.append(events[i, 0])
                
#     # Remove the first 12 D4_stim events if they exist
#     D4_stim = D4_stim[12:] if len(D4_stim) > 12 else []

#     return np.array(D4_stim), np.array(D4_rest)

# def split_d4_blocks(D4_stim, sfreq=3000, block_duration_sec=60, min_block_length=10):
#     """
#     Split D4_stim array into D4_pulse_blocks and D4_rest_blocks based on intervals and block length.
    
#     Parameters:
#     - D4_stim: Numpy array of sample indices (1D array).
#     - sfreq: Sampling frequency in Hz (default 3000 Hz).
#     - block_duration_sec: Time in seconds used as a threshold to define new blocks (default 60s).
#     - min_block_length: Minimum number of samples to consider as a valid block (default 10 samples).
    
#     Returns:
#     - D4_pulse_blocks: Numpy array of pulse blocks.
#     - D4_rest_blocks: Numpy array of rest blocks.
#     """
#     # Convert the block duration to samples
#     block_duration_samples = block_duration_sec * sfreq
    
#     # Initialize variables
#     D4_pulse_blocks = []
#     D4_rest_blocks = []
#     current_block = []
    
#     # Iterate over D4_stim to identify blocks
#     for i in range(1, len(D4_stim)):
#         # Calculate the interval between consecutive D4_stim samples
#         interval = D4_stim[i] - D4_stim[i - 1]
        
#         # Add the current sample to the current block
#         current_block.append(D4_stim[i - 1])
        
#         # If the interval is larger than the threshold, process the current block
#         if interval > block_duration_samples:
#             if len(current_block) >= min_block_length:
#                 # Alternate between pulse and rest blocks
#                 if len(D4_rest_blocks) <= len(D4_pulse_blocks):
#                     D4_rest_blocks.extend(current_block)
#                 else:
#                     D4_pulse_blocks.extend(current_block)
#             # Start a new block
#             current_block = []
    
#     # Add the last block if it meets the minimum block length
#     if len(current_block) >= min_block_length:
#         if len(D4_rest_blocks) <= len(D4_pulse_blocks):
#             D4_rest_blocks.extend(current_block)
#         else:
#             D4_pulse_blocks.extend(current_block)
    
#     # Convert lists to numpy arrays
#     return np.array(D4_pulse_blocks), np.array(D4_rest_blocks)

# def split_into_blocks(data, sfreq=3000, block_duration_sec=60, min_block_length=10):
#     """
#     General function to split a 1D array of sample indices into pulse and rest blocks based on intervals and block length.
    
#     Parameters:
#     - data: Numpy array of sample indices (1D array).
#     - sfreq: Sampling frequency in Hz (default 3000 Hz).
#     - block_duration_sec: Time in seconds used as a threshold to define new blocks (default 60s).
#     - min_block_length: Minimum number of samples to consider as a valid block (default 10 samples).
    
#     Returns:
#     - pulse_blocks: Numpy array of pulse blocks.
#     - rest_blocks: Numpy array of rest blocks.
#     """
#     block_duration_samples = block_duration_sec * sfreq
#     pulse_blocks = []
#     rest_blocks = []
#     current_block = []
    
#     for i in range(1, len(data)):
#         interval = data[i] - data[i - 1]
#         current_block.append(data[i - 1])
        
#         if interval > block_duration_samples:
#             if len(current_block) >= min_block_length:
#                 if len(rest_blocks) <= len(pulse_blocks):
#                     rest_blocks.extend(current_block)
#                 else:
#                     pulse_blocks.extend(current_block)
#             current_block = []
    
#     if len(current_block) >= min_block_length:
#         if len(rest_blocks) <= len(pulse_blocks):
#             rest_blocks.extend(current_block)
#         else:
#             pulse_blocks.extend(current_block)
    
#     return np.array(pulse_blocks), np.array(rest_blocks)

# def identify_blocks(data, sfreq=3000, block_duration_sec=60, min_block_length=10):
#     block_duration_samples = block_duration_sec * sfreq
#     block_number = []
#     current_block = []
#     block_id = 1  # Start with block 1

#     for i in range(1, len(data)):
#         interval = data[i] - data[i - 1]
#         current_block.append(data[i - 1])

#         if interval > block_duration_samples:
#             # Assign block_id if the current block meets min_block_length
#             if len(current_block) >= min_block_length:
#                 block_number.extend([block_id] * len(current_block))
#                 block_id += 1  # Move to the next block
#             else:
#                 # Use 0 for sequences that don’t meet min_block_length
#                 block_number.extend([0] * len(current_block))
#             current_block = []  # Reset for the next potential block

#     # Final check for the last block
#     current_block.append(data[-1])
#     if len(current_block) >= min_block_length:
#         block_number.extend([block_id] * len(current_block))
#     else:
#         block_number.extend([0] * len(current_block))

#     return np.array(block_number)

# ----------------------------------------------------------------------------------
# # MEP peak-to-peak function 
# def peak_to_peak_amplitude(input_signal):
#     """Compute peak to peak amplitude in signal; i.e. max - min."""
#     min_v = np.min(input_signal, axis=0)
#     max_v = np.max(input_signal, axis=0)
#     peak_to_peak = max_v - min_v
#     return peak_to_peak


def peak_to_peak_amplitude(input_signal, delay_ms=10, sampling_frequency=3000):
    """
    Compute the peak-to-peak amplitude of a signal starting after a specified delay.

    This function calculates the difference between the maximum and minimum values 
    of the input signal, but only considers data points that occur after a specified 
    delay in milliseconds. This is useful for excluding any artifacts or noise 
    present in the initial part of the signal.

    Parameters:
    -----------
    input_signal : numpy.ndarray
        A 1D or 2D array containing the signal data. If 2D, each column is treated 
        as a separate channel.
    
    delay_ms : int, optional
        The delay in milliseconds after which to start calculating the peak-to-peak 
        amplitude. Default is 10 ms.
    
    sampling_frequency : int, optional
        The sampling frequency of the signal in Hz. Default is 3000 Hz.

    Returns:
    --------
    numpy.ndarray
        The peak-to-peak amplitude for each channel in the input signal, calculated 
        from the data starting after the specified delay.
    """
    
    # Convert delay from milliseconds to samples
    delay_samples = int(delay_ms * (sampling_frequency / 1000))
    
    # Slice the input_signal to start after the specified delay
    delayed_signal = input_signal[delay_samples:]

    # Calculate min and max for the delayed signal
    min_v = np.min(delayed_signal, axis=0)
    max_v = np.max(delayed_signal, axis=0)
    
    # Calculate peak-to-peak amplitude
    peak_to_peak = max_v - min_v
    return peak_to_peak


# RMS function
def rms_amplitude(input_signal):
    """Compute RMS amplitude in signal."""
    rms = np.sqrt(np.mean(input_signal**2, axis=0))
    return rms

def get_event_data_windows(data_filtered, events_D4, samples_before_stim, samples_after_stim, samples_before_rms):
    """Extract data windows for peak-to-peak and RMS processing."""
    p2p_1, p2p_2, rms_1, rms_2 = [], [], [], []

    for i in range(len(events_D4)):
        win_1 = data_filtered._data[0][events_D4[i] - samples_before_stim : events_D4[i] + samples_after_stim]
        win_2 = data_filtered._data[1][events_D4[i] - samples_before_stim : events_D4[i] + samples_after_stim]

        rms_win_1 = data_filtered._data[0][events_D4[i] - samples_before_rms : events_D4[i]]
        rms_win_2 = data_filtered._data[1][events_D4[i] - samples_before_rms : events_D4[i]]

        p2p_1.append(peak_to_peak_amplitude(win_1))
        p2p_2.append(peak_to_peak_amplitude(win_2))
        rms_1.append(rms_amplitude(rms_win_1))
        rms_2.append(rms_amplitude(rms_win_2))

    return np.array(p2p_1), np.array(p2p_2), np.array(rms_1), np.array(rms_2)

def exclude_mep_rms(data, rms_values, rms_threshold):
    """
    Apply exclusion criteria to MEP data based on RMS thresholds.

    This function modifies the input MEP data by setting values to NaN
    wherever the corresponding RMS values exceed a given threshold.
    Parameters:
    -----------
    data : numpy.ndarray
        A 1D or 2D array containing the MEP data. The function modifies this array 
        in place based on the exclusion criteria.

    rms_values : numpy.ndarray
        A 1D or 2D array containing the RMS values corresponding to the MEP data. 
        This array should have the same shape as `data`.

    rms_threshold : float
        The threshold value above which RMS values will trigger exclusion in the MEP data.

    symbolic_value : int, optional
        The value to assign to elements in `data` where the corresponding RMS values 
        exceed the threshold. Default is 99900.

    Returns:
    --------
    numpy.ndarray
        The modified MEP data array with values set to `symbolic_value` where 
        RMS values exceed the specified threshold.
    """
    
    # Apply exclusion criteria
    # excluded_data = data[rms_values > rms_threshold]
    data[rms_values > rms_threshold] = np.nan
    return data #, excluded_data

# def exclude_low_meps(reference_array, target_array, num_sd=3):
#     """
#     Filters the target array by replacing values below (mean - num_sd * std_dev)
#     of the reference array with a nan.

#     Parameters:
#         reference_array (np.ndarray): Array used to calculate mean and standard deviation.
#         target_array (np.ndarray): Array to be filtered.
#         num_sd (float): Number of standard deviations to determine the threshold. Default is 3.
        
#     Returns:
#         np.ndarray: Filtered version of the target array.
#     """
#     # Calculate mean and standard deviation of the reference array
#     mean_ref = np.mean(reference_array)
#     std_ref = np.std(reference_array)

#     # Calculate threshold
#     threshold = mean_ref - num_sd * std_ref

#     # Filter target array
#     #excluded_array = target_array[target_array < threshold]
#     filtered_array = np.where(target_array < threshold, np.nan, target_array)

#     return filtered_array #, excluded_array

# def calculate_relative_mep(p2p_values):
#     """
#     Calculate relative MEP amplitudes.
#     """
#     mean_value = np.nanmean(p2p_values)
#     relative_mep = p2p_values / mean_value
#     return relative_mep

def normalize_mep_by_mean(array1, array2):
    """
    Calculate an array where each value of array1 is divided by the mean
    of valid values based on specific rules.

    Parameters:
    array1 (np.ndarray): The first array containing numerical values.
    array2 (np.ndarray): The second array containing values from 0 to 6.

    Returns:
    np.ndarray: An array with each value of array1 divided by the calculated mean,
                or None if no valid values are found.
    """
    
    # Create a mask for values < 5000 in array1
    mask = (array1 < 5000)
    
    # Create a mask for values in array2 that are either 2, 4, or 6
    filter_mask = np.isin(array2, [2, 4, 6])
    
    # Combine masks to get valid indices
    valid_indices = mask & filter_mask
    
    # Get the filtered values from array1
    filtered_values = array1[valid_indices]
    
    # Calculate the mean of the filtered values
    mean_value = np.mean(filtered_values)
        
    # Create array3 by dividing each value in array1 by the mean
    array3 = array1 / mean_value
    
    return array3

# def exclude_by_iqr(data_array, index_array, ref_blocks=[2, 4, 6], iqr_multiplier=1.5):
#     """
#     Processes array using IQR-based outlier detection based on indexed reference blocks
    
#     Parameters:
#     data_array (array-like): Input data array to be processed
#     index_array (array-like): Array of indices indicating block numbers
#     ref_blocks (list): Reference blocks for filtering (default: [2, 4, 6])
#     iqr_multiplier (float): IQR multiplier for outlier threshold (default: 1.5)
    
#     Returns:
#     array: Processed array with outliers as NaNs only in reference blocks
#     """
#     # Convert inputs to numpy arrays with explicit typing
#     data = np.array(data_array, dtype=np.float64)
#     indices = np.array(index_array, dtype=np.int64)
    
#     # Verify arrays have same length
#     if len(data) != len(indices):
#         raise ValueError("Data array and index array must have the same length")
    
#     # Create boolean mask for reference blocks
#     block_mask = np.isin(indices, ref_blocks)
    
#     def calculate_iqr_bounds(values, mask):
#         """Calculate IQR-based exclusion bounds for an array"""
#         masked_data = values[mask]
#         if masked_data.size < 4:  # Not enough data for meaningful quartile calculation
#             return (-np.inf, np.inf)
            
#         q1 = np.nanpercentile(masked_data, 25)
#         q3 = np.nanpercentile(masked_data, 75)
#         iqr = q3 - q1
#         return (q1 - iqr_multiplier * iqr, q3 + iqr_multiplier * iqr)
    
#     # Calculate bounds using only the values in reference blocks
#     lower, upper = calculate_iqr_bounds(data, block_mask)
    
#     # Create copy with exclusions marked as NaN
#     processed_arr = data.copy()
#     # Only replace values in reference blocks that are outside the bounds
#     outlier_mask = (data < lower) | (data > upper)
#     processed_arr[block_mask & outlier_mask] = np.nan
    
#     return processed_arr

def remove_outliers_by_index(data, index_array):
    """
    Remove outliers from data array but only for specific index values (2, 4, 6)
    using the IQR method.
    
    Parameters:
    data (array-like): Array containing the values
    index_array (array-like): Array containing index values
    
    Returns:
    numpy.ndarray: Array with outliers replaced by nan for specified indices
    """
    # Convert inputs to numpy arrays
    data = np.array(data, dtype=float)
    index_array = np.array(index_array)
    
    # Create a mask for the indices we want to process (2, 4, 6)
    target_indices = np.isin(index_array, [2, 4, 6])
    
    # Get the values we want to process
    values_to_process = data[target_indices]
    
    if len(values_to_process) > 0:  # Only proceed if we have values to process
        # Calculate Q1, Q3 and IQR for the selected values
        Q1 = np.percentile(values_to_process, 25)
        Q3 = np.percentile(values_to_process, 75)
        IQR = Q3 - Q1
        
        # Define bounds
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # Create a copy of the original data
        result = data.copy()
        
        # Replace outliers with nan only for the specified indices
        mask = target_indices & ((data < lower_bound) | (data > upper_bound))
        result[mask] = np.nan
        
        return result
    
    return data  # Return original data if no values to process