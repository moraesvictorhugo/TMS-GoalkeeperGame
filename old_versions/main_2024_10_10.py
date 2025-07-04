"""
=================================================
Main Script
=================================================
"""
from modules import import_signal
from modules import signal_processing
from modules import plot_data
from modules import export_data
from modules import utils
import numpy as np
import mne
import matplotlib
matplotlib.use('TkAgg')  # install python3-pil.imagetk if required

"""
============================================
STEP 0 - Importing Data and Setting Flags
============================================
"""
# Setting flags
volunteer_number = 'V04'  # Change volunteer number for analysis
bool_export = True  # Change to export data to CSV
bool_plots = True   # Change to plot data
normalization = 'normalize_by_mean'  # Choose between (normalize_by_rest, zscore, normalize_by_mean)
rms_thresh = 2     # in standard deviations. Used for both FDI and FDS exclusion criteria
# bool_exclude_familiarization = False # Change to remove 12 first trials

# Importing data
fname = import_signal.find_vhdr_file(volunteer_number)
raw = import_signal.import_brainvision_data(fname)

"""
============================================
STEP 1 - Signal Processing
============================================
"""
## Downsampling and ploting spectral analysis
raw = signal_processing.downsample_data(raw)

## Notch filtering and ploting
raw_notch = signal_processing.notch_filter_data(raw)
# if bool_plots:
#     plot_data.plot_spectrum_amplitude(raw_notch, channel_index=0, fmin=1, fmax=600)
#     plot_data.plot_psd(raw_notch)

## Bandpass filtering
bandpass_filter = signal_processing.apply_bandpass_filter(raw_notch, l_freq=20, h_freq=500)
data_filtered = signal_processing.create_filtered_raw_object(bandpass_filter, raw_notch.info)
# if bool_plots:
#     plot_data.plot_spectrum_amplitude(data_filtered, channel_index=0, fmin=1, fmax=600)
#     plot_data.plot_psd(data_filtered)

# Add annotations from the original raw data and plot filtered data
data_filtered = utils.add_annotations_to_filtered(data_filtered, raw_notch)
# if bool_plots:
#     data_filtered.plot()

## Verify markers
utils.marker_verification(raw, data_filtered)
events_from_annot, event_dict = mne.events_from_annotations(data_filtered)
if bool_plots:
    mne.viz.plot_events(events_from_annot, sfreq=data_filtered.info['sfreq'], event_id=event_dict)
    
"""
====================================================
STEP 2 - Block Identification and General Parameters
====================================================
"""
# Split blocks and samples by annotations (D3)
(
    events_from_annot_block1, events_from_annot_block2, events_from_annot_block3, 
    events_from_annot_block4, events_from_annot_block5, events_from_annot_block6
) = signal_processing.split_events_into_blocks(
    events_from_annot, 
    event_id=3
)

# Plot to verify event blocks
if bool_plots:
    event_blocks = [
        events_from_annot_block1,
        events_from_annot_block2,
        events_from_annot_block3,
        events_from_annot_block4,
        events_from_annot_block5,
        events_from_annot_block6
    ]
    plot_data.plot_event_blocks(event_blocks, sfreq=data_filtered.info['sfreq'])

# Create the trigger array
trigger = signal_processing.create_trigger_array(data_filtered)

# Get sampling frequency and set timing variables
sfreq = int(data_filtered.info["sfreq"])
time_before_stim = 0.01  # s
time_after_stim = 0.1  # s
time_before_rms = 0.5  # s

# Compute sample counts for window rms and MEP analysis
samples_before_stim = int(time_before_stim * sfreq)
samples_after_stim = int(time_after_stim * sfreq)
samples_before_rms = int(time_before_rms * sfreq)

# Conversion of code names ('Gkg/G 2', 'Gkg/G 4' and 'Gkg/G 8') to alfabet numbers (0, 1 and 2)
alfabet = {
    'Gkg/G  2': 0,
    'Gkg/G  4': 1,
    'Gkg/G  8': 2
}

"""
============================================
STEP 3 - Event Analysis for Block 2 
============================================
"""
# Extract events from annotations of block 2 based on event_id
events_from_annot_D1_block2 = utils.extract_events_from_annot(events_from_annot_block2, 3)
events_from_annot_D2_block2 = utils.extract_events_from_annot(events_from_annot_block2, 2)
events_from_annot_G2_block2 = utils.extract_events_from_annot(events_from_annot_block2, 6)
events_from_annot_G4_block2 = utils.extract_events_from_annot(events_from_annot_block2, 7)
events_from_annot_G8_block2 = utils.extract_events_from_annot(events_from_annot_block2, 8)
events_from_annot_D4_block2 = utils.extract_events_from_annot(events_from_annot_block2, 4)

# Combine Gkg events of block 2
events_Gkg_block2 = utils.combine_gkg_events(events_from_annot_G2_block2, events_from_annot_G4_block2, events_from_annot_G8_block2)

# Calculate response times
response_times_block2, sequence_block2, choice_block2 = signal_processing.calculate_response_times(
    events_from_annot_D2_block2, events_Gkg_block2, data_filtered)

# Get sequence and choice from block 2
sequence_block2 = utils.convert_to_alfabet(sequence_block2, alfabet)  # convert Gx1 (sequence) to alfabet numbers
choice_block2 = utils.convert_to_alfabet(choice_block2, alfabet)  # convert Gx2 (choice) to alfabet numbers

# Analyse choices
result_block2 = signal_processing.analyze_choice(choice_block2, sequence_block2)

"""
============================================
STEP 4 - MEP and RMS Analysis for Block 2
============================================
"""
# Detect events 'Display/D 4' for Trigger
events_D4_block2 = events_from_annot_D4_block2[:, 0]

# Create figure for plotting
f, ax1, ax2 = plot_data.create_figure("MEPs in Block 2")

# Create x-axis (time) values
x = np.arange(-time_before_stim, time_after_stim, 1/sfreq)

# Process event windows and get MEP and RMS
MEPpp_FDI_block2_V, MEPpp_FDS_block2_V, rmsAmplitude_FDI_block2_V, rmsAmplitude_FDS_block2_V = signal_processing.get_event_data_windows(
    data_filtered, events_D4_block2, samples_before_stim, samples_after_stim, samples_before_rms
)

# Plot the extracted data
for i in range(len(events_D4_block2)):
    win_1 = data_filtered._data[0][events_D4_block2[i] - samples_before_stim : events_D4_block2[i] + samples_after_stim]
    win_2 = data_filtered._data[1][events_D4_block2[i] - samples_before_stim : events_D4_block2[i] + samples_after_stim]
    plot_data.plot_emg_data(x, data_filtered, win_1, win_2, ax1, ax2)

# Configure and display the plot
if bool_plots:
    plot_data.configure_plot(data_filtered, ax1, ax2)

# Analyze amplitudes
rms_mean_FDI_block2 = np.mean(rmsAmplitude_FDI_block2_V)
rms_mean_FDS_block2 = np.mean(rmsAmplitude_FDS_block2_V)
rms_std_FDI_block2 = np.std(rmsAmplitude_FDI_block2_V)
rms_std_FDS_block2 = np.std(rmsAmplitude_FDS_block2_V)

# Set RMS thresholds for exclusion
rms_threshold_FDI = rms_mean_FDI_block2 + (rms_thresh * rms_std_FDI_block2)
rms_threshold_FDS = rms_mean_FDS_block2 + (rms_thresh * rms_std_FDS_block2)

"""
=============================================================
STEP 5 - Analysis of RMS values and MEP Exclusion for Block 2
=============================================================
"""
# Get RMS time points
rms_time_points_block2 = data_filtered.times[events_D4_block2]

# Plot RMS amplitudes
if bool_plots:
    plot_data.plot_rms_amplitudes(
        rms_time_points_block2, rmsAmplitude_FDI_block2_V, rmsAmplitude_FDS_block2_V, rms_threshold_FDI, rms_threshold_FDS,
        data_filtered)

# Plot MEP amplitudes
if bool_plots:
    plot_data.plot_mep_amplitudes(
        rms_time_points_block2, MEPpp_FDI_block2_V, MEPpp_FDS_block2_V, rmsAmplitude_FDI_block2_V, rmsAmplitude_FDS_block2_V, rms_threshold_FDI, 
        rms_threshold_FDS, data_filtered)

# Apply exclusion to MEP amplitudes based on RMS
MEPpp_FDI_withExclusions_block2_V = signal_processing.exclude_mep_rms(MEPpp_FDI_block2_V.copy(), rmsAmplitude_FDI_block2_V, rms_threshold_FDI)
MEPpp_FDS_withExclusions_block2_V = signal_processing.exclude_mep_rms(MEPpp_FDS_block2_V.copy(), rmsAmplitude_FDS_block2_V, rms_threshold_FDS)

# Plot MEP vs RMS amplitudes (with and without exclusion)
if bool_plots:
    plot_data.plot_mep_vs_rms(rmsAmplitude_FDI_block2_V, rmsAmplitude_FDS_block2_V, MEPpp_FDI_block2_V, MEPpp_FDS_block2_V)

# Indices where MEPs were excluded
excluded_indices_FDI_block2 = np.where(~np.isnan(MEPpp_FDI_withExclusions_block2_V))[0]
excluded_indices_FDS_block2 = np.where(~np.isnan(MEPpp_FDS_withExclusions_block2_V))[0]

# Plot MEP vs RMS for excluded data
if bool_plots:
    plot_data.plot_excluded_mep_vs_rms(
        rmsAmplitude_FDI_block2_V, rmsAmplitude_FDS_block2_V, MEPpp_FDI_withExclusions_block2_V, MEPpp_FDS_withExclusions_block2_V, excluded_indices_FDI_block2,
        excluded_indices_FDS_block2)
    
"""
============================================
STEP 6 - Event Analysis for Block 4 
============================================
"""
# Extract events from annotations of Block 4 based on event_id
events_from_annot_D1_block4 = utils.extract_events_from_annot(events_from_annot_block4, 3)
events_from_annot_D2_block4 = utils.extract_events_from_annot(events_from_annot_block4, 2)
events_from_annot_G2_block4 = utils.extract_events_from_annot(events_from_annot_block4, 6)
events_from_annot_G4_block4 = utils.extract_events_from_annot(events_from_annot_block4, 7)
events_from_annot_G8_block4 = utils.extract_events_from_annot(events_from_annot_block4, 8)
events_from_annot_D4_block4 = utils.extract_events_from_annot(events_from_annot_block4, 4)

# Combine Gkg events of Block 4
events_Gkg_block4 = utils.combine_gkg_events(events_from_annot_G2_block4, events_from_annot_G4_block4, events_from_annot_G8_block4)

# Calculate response times
response_times_block4, sequence_block4, choice_block4 = signal_processing.calculate_response_times(
    events_from_annot_D2_block4, events_Gkg_block4, data_filtered)

# Get sequence and choice from Block 4
sequence_block4 = utils.convert_to_alfabet(sequence_block4, alfabet)  # convert Gx1 (sequence) to alfabet numbers
choice_block4 = utils.convert_to_alfabet(choice_block4, alfabet)  # convert Gx2 (choice) to alfabet numbers

# Analyse choices
result_block4 = signal_processing.analyze_choice(choice_block4, sequence_block4)

"""
============================================
STEP 7 - MEP and RMS Analysis for Block 4
============================================
"""
# Detect events 'Display/D 4' for Trigger
events_D4_block4 = events_from_annot_D4_block4[:, 0]

# Create figure for plotting
f, ax1, ax2 = plot_data.create_figure("MEPs in Block 4")

# Create x-axis (time) values
x = np.arange(-time_before_stim, time_after_stim, 1/sfreq)

# Process event windows and get MEP and RMS
MEPpp_FDI_block4_V, MEPpp_FDS_block4_V, rmsAmplitude_FDI_block4_V, rmsAmplitude_FDS_block4_V = signal_processing.get_event_data_windows(
    data_filtered, events_D4_block4, samples_before_stim, samples_after_stim, samples_before_rms
)

# Plot the extracted data
for i in range(len(events_D4_block4)):
    win_1 = data_filtered._data[0][events_D4_block4[i] - samples_before_stim : events_D4_block4[i] + samples_after_stim]
    win_2 = data_filtered._data[1][events_D4_block4[i] - samples_before_stim : events_D4_block4[i] + samples_after_stim]
    plot_data.plot_emg_data(x, data_filtered, win_1, win_2, ax1, ax2)

# Configure and display the plot
if bool_plots:
    plot_data.configure_plot(data_filtered, ax1, ax2)

# Analyze amplitudes
rms_mean_FDI_block4 = np.mean(rmsAmplitude_FDI_block4_V)
rms_mean_FDS_block4 = np.mean(rmsAmplitude_FDS_block4_V)
rms_std_FDI_block4 = np.std(rmsAmplitude_FDI_block4_V)
rms_std_FDS_block4 = np.std(rmsAmplitude_FDS_block4_V)

# Set RMS thresholds for exclusion
rms_threshold_FDI = rms_mean_FDI_block4 + (rms_thresh * rms_std_FDI_block4)
rms_threshold_FDS = rms_mean_FDS_block4 + (rms_thresh * rms_std_FDS_block4)

"""
=============================================================
STEP 8 - Analysis of RMS values and MEP Exclusion for Block 4
=============================================================
"""
# Get RMS time points
rms_time_points_block4 = data_filtered.times[events_D4_block4]

# Plot RMS amplitudes
if bool_plots:
    plot_data.plot_rms_amplitudes(
        rms_time_points_block4, rmsAmplitude_FDI_block4_V, rmsAmplitude_FDS_block4_V, rms_threshold_FDI, rms_threshold_FDS,
        data_filtered)

# Plot MEP amplitudes
if bool_plots:
    plot_data.plot_mep_amplitudes(
        rms_time_points_block4, MEPpp_FDI_block4_V, MEPpp_FDS_block4_V, rmsAmplitude_FDI_block4_V, rmsAmplitude_FDS_block4_V, rms_threshold_FDI, 
        rms_threshold_FDS, data_filtered)

# Apply exclusion to MEP amplitudes based on RMS
MEPpp_FDI_withExclusions_block4_V = signal_processing.exclude_mep_rms(MEPpp_FDI_block4_V.copy(), rmsAmplitude_FDI_block4_V, rms_threshold_FDI)
MEPpp_FDS_withExclusions_block4_V = signal_processing.exclude_mep_rms(MEPpp_FDS_block4_V.copy(), rmsAmplitude_FDS_block4_V, rms_threshold_FDS)

# Plot MEP vs RMS amplitudes (with and without exclusion)
if bool_plots:
    plot_data.plot_mep_vs_rms(rmsAmplitude_FDI_block4_V, rmsAmplitude_FDS_block4_V, MEPpp_FDI_block4_V, MEPpp_FDS_block4_V)

# Indices where MEPs were excluded
excluded_indices_FDI_block4 = np.where(~np.isnan(MEPpp_FDI_withExclusions_block4_V))[0]
excluded_indices_FDS_block4 = np.where(~np.isnan(MEPpp_FDS_withExclusions_block4_V))[0]

# Plot MEP vs RMS for excluded data
if bool_plots:
    plot_data.plot_excluded_mep_vs_rms(
        rmsAmplitude_FDI_block4_V, rmsAmplitude_FDS_block4_V, MEPpp_FDI_withExclusions_block4_V, MEPpp_FDS_withExclusions_block4_V, excluded_indices_FDI_block4,
        excluded_indices_FDS_block4)

"""
============================================
STEP 9 - Event Analysis for Block 6 
============================================
"""
# Extract events from annotations of Block 6 based on event_id
events_from_annot_D1_block6 = utils.extract_events_from_annot(events_from_annot_block6, 3)
events_from_annot_D2_block6 = utils.extract_events_from_annot(events_from_annot_block6, 2)
events_from_annot_G2_block6 = utils.extract_events_from_annot(events_from_annot_block6, 6)
events_from_annot_G4_block6 = utils.extract_events_from_annot(events_from_annot_block6, 7)
events_from_annot_G8_block6 = utils.extract_events_from_annot(events_from_annot_block6, 8)
events_from_annot_D4_block6 = utils.extract_events_from_annot(events_from_annot_block6, 4)

# Combine Gkg events of Block 6
events_Gkg_block6 = utils.combine_gkg_events(events_from_annot_G2_block6, events_from_annot_G4_block6, events_from_annot_G8_block6)

# Calculate response times
response_times_block6, sequence_block6, choice_block6 = signal_processing.calculate_response_times(
    events_from_annot_D2_block6, events_Gkg_block6, data_filtered)

# Get sequence and choice from Block 6
sequence_block6 = utils.convert_to_alfabet(sequence_block6, alfabet)  # convert Gx1 (sequence) to alfabet numbers
choice_block6 = utils.convert_to_alfabet(choice_block6, alfabet)  # convert Gx2 (choice) to alfabet numbers

# Analyse choices
result_block6 = signal_processing.analyze_choice(choice_block6, sequence_block6)

"""
============================================
STEP 10 - MEP and RMS Analysis for Block 6
============================================
"""
# Detect events 'Display/D 4' for Trigger
events_D4_block6 = events_from_annot_D4_block6[:, 0]

# Create figure for plotting
f, ax1, ax2 = plot_data.create_figure("MEPs in Block 6")

# Create x-axis (time) values
x = np.arange(-time_before_stim, time_after_stim, 1/sfreq)

# Process event windows and get MEP and RMS
MEPpp_FDI_block6_V, MEPpp_FDS_block6_V, rmsAmplitude_FDI_block6_V, rmsAmplitude_FDS_block6_V = signal_processing.get_event_data_windows(
    data_filtered, events_D4_block6, samples_before_stim, samples_after_stim, samples_before_rms
)

# Plot the extracted data
for i in range(len(events_D4_block6)):
    win_1 = data_filtered._data[0][events_D4_block6[i] - samples_before_stim : events_D4_block6[i] + samples_after_stim]
    win_2 = data_filtered._data[1][events_D4_block6[i] - samples_before_stim : events_D4_block6[i] + samples_after_stim]
    plot_data.plot_emg_data(x, data_filtered, win_1, win_2, ax1, ax2)

# Configure and display the plot
if bool_plots:
    plot_data.configure_plot(data_filtered, ax1, ax2)

# Analyze amplitudes
rms_mean_FDI_block6 = np.mean(rmsAmplitude_FDI_block6_V)
rms_mean_FDS_block6 = np.mean(rmsAmplitude_FDS_block6_V)
rms_std_FDI_block6 = np.std(rmsAmplitude_FDI_block6_V)
rms_std_FDS_block6 = np.std(rmsAmplitude_FDS_block6_V)

# Set RMS thresholds for exclusion
rms_threshold_FDI = rms_mean_FDI_block6 + (rms_thresh * rms_std_FDI_block6)
rms_threshold_FDS = rms_mean_FDS_block6 + (rms_thresh * rms_std_FDS_block6)

"""
=============================================================
STEP 11 - Analysis of RMS values and MEP Exclusion for Block 6
=============================================================
"""
# Get RMS time points
rms_time_points_block6 = data_filtered.times[events_D4_block6]

# Plot RMS amplitudes
if bool_plots:
    plot_data.plot_rms_amplitudes(
        rms_time_points_block6, rmsAmplitude_FDI_block6_V, rmsAmplitude_FDS_block6_V, rms_threshold_FDI, rms_threshold_FDS,
        data_filtered)

# Plot MEP amplitudes
if bool_plots:
    plot_data.plot_mep_amplitudes(
        rms_time_points_block6, MEPpp_FDI_block6_V, MEPpp_FDS_block6_V, rmsAmplitude_FDI_block6_V, rmsAmplitude_FDS_block6_V, rms_threshold_FDI, 
        rms_threshold_FDS, data_filtered)

# Apply exclusion to MEP amplitudes based on RMS
MEPpp_FDI_withExclusions_block6_V = signal_processing.exclude_mep_rms(MEPpp_FDI_block6_V.copy(), rmsAmplitude_FDI_block6_V, rms_threshold_FDI)
MEPpp_FDS_withExclusions_block6_V = signal_processing.exclude_mep_rms(MEPpp_FDS_block6_V.copy(), rmsAmplitude_FDS_block6_V, rms_threshold_FDS)

# Plot MEP vs RMS amplitudes (with and without exclusion)
if bool_plots:
    plot_data.plot_mep_vs_rms(rmsAmplitude_FDI_block6_V, rmsAmplitude_FDS_block6_V, MEPpp_FDI_block6_V, MEPpp_FDS_block6_V)

# Indices where MEPs were excluded
excluded_indices_FDI_block6 = np.where(~np.isnan(MEPpp_FDI_withExclusions_block6_V))[0]
excluded_indices_FDS_block6 = np.where(~np.isnan(MEPpp_FDS_withExclusions_block6_V))[0]

# Plot MEP vs RMS for excluded data
if bool_plots:
    plot_data.plot_excluded_mep_vs_rms(
        rmsAmplitude_FDI_block6_V, rmsAmplitude_FDS_block6_V, MEPpp_FDI_withExclusions_block6_V, MEPpp_FDS_withExclusions_block6_V, excluded_indices_FDI_block6,
        excluded_indices_FDS_block6)

"""
============================================
STEP 12 - MEP normalization
============================================
"""
if normalization == 'normalize_by_mean':
    relative_MEPpp_FDI_withExclusions_block2 = signal_processing.calculate_relative_mep_bymean(MEPpp_FDI_withExclusions_block2_V, MEPpp_FDI_withExclusions_block6_V, MEPpp_FDI_withExclusions_block4_V)
    relative_MEPpp_FDS_withExclusions_block2 = signal_processing.calculate_relative_mep_bymean(MEPpp_FDS_withExclusions_block2_V, MEPpp_FDS_withExclusions_block6_V, MEPpp_FDS_withExclusions_block4_V)
    relative_MEPpp_FDI_withExclusions_block4 = signal_processing.calculate_relative_mep_bymean(MEPpp_FDI_withExclusions_block4_V, MEPpp_FDI_withExclusions_block6_V, MEPpp_FDI_withExclusions_block2_V)
    relative_MEPpp_FDS_withExclusions_block4 = signal_processing.calculate_relative_mep_bymean(MEPpp_FDS_withExclusions_block4_V, MEPpp_FDS_withExclusions_block6_V, MEPpp_FDS_withExclusions_block2_V)   
    relative_MEPpp_FDI_withExclusions_block6 = signal_processing.calculate_relative_mep_bymean(MEPpp_FDI_withExclusions_block6_V, MEPpp_FDI_withExclusions_block2_V, MEPpp_FDI_withExclusions_block4_V)
    relative_MEPpp_FDS_withExclusions_block6 = signal_processing.calculate_relative_mep_bymean(MEPpp_FDS_withExclusions_block6_V, MEPpp_FDS_withExclusions_block2_V, MEPpp_FDS_withExclusions_block4_V)

"""
============================================
STEP 13 - Plots of Raw Signals
============================================
"""
if bool_plots:
    # Simple bar plot for comparison between FDI in different blocks
    # Plot the bar chart with error bars
    labels = ['Block 2', 'Block 4', 'Block 6']    
    plot_data.plot_bar_with_sd(
        relative_MEPpp_FDI_withExclusions_block2, relative_MEPpp_FDI_withExclusions_block4,
        relative_MEPpp_FDI_withExclusions_block6, labels, title='Relative MEPs by blocks')




# # List of variables and names for histogram plotting
# main_variables = [rmsAmplitude_FDI_V, rmsAmplitude_FDS_V, MEPpp_FDI_V, MEPpp_FDS_V]
# variable_names = ['rms_FDI', 'rms_FDS', 'MEPpp_FDI_V', 'MEPpp_FDS_V']

# # Plot histograms
# if bool_plots:
#     plot_data.plot_multiple_histograms(variable_names, main_variables)


# Criar novamente scatter para os 3 blocos juntos como tínhamos antes

"""
============================================
STEP 14 - Data Handling for Exportation
============================================
"""
# Group variables for export
variables_to_export_summary = {
    'rmsAmplitude_FDI_block2_V': rmsAmplitude_FDI_block2_V,
    'rmsAmplitude_FDS_block2_V': rmsAmplitude_FDS_block2_V,
    'MEPpp_FDI_withExclusions_block2_V': MEPpp_FDI_withExclusions_block2_V,
    'MEPpp_FDS_withExclusions_block2_V': MEPpp_FDS_withExclusions_block2_V,
    'relative_MEPpp_FDI_withExclusions_block2': relative_MEPpp_FDI_withExclusions_block2,
    'relative_MEPpp_FDS_withExclusions_block2': relative_MEPpp_FDS_withExclusions_block2,
    'sequence_block2': sequence_block2,
    'choice_block2': choice_block2,
    'result_block2': result_block2,
    'response_times_block2': response_times_block2,
    
    # Block 4
    'rmsAmplitude_FDI_block4_V': rmsAmplitude_FDI_block4_V,
    'rmsAmplitude_FDS_block4_V': rmsAmplitude_FDS_block4_V,
    'MEPpp_FDI_withExclusions_block4_V': MEPpp_FDI_withExclusions_block4_V,
    'MEPpp_FDS_withExclusions_block4_V': MEPpp_FDS_withExclusions_block4_V,
    'relative_MEPpp_FDI_withExclusions_block4': relative_MEPpp_FDI_withExclusions_block4,
    'relative_MEPpp_FDS_withExclusions_block4': relative_MEPpp_FDS_withExclusions_block4,
    'sequence_block4': sequence_block4,
    'choice_block4': choice_block4,
    'result_block4': result_block4,
    'response_times_block4': response_times_block4,
    
    # Block 6
    'rmsAmplitude_FDI_block6_V': rmsAmplitude_FDI_block6_V,
    'rmsAmplitude_FDS_block6_V': rmsAmplitude_FDS_block6_V,
    'MEPpp_FDI_withExclusions_block6_V': MEPpp_FDI_withExclusions_block6_V,
    'MEPpp_FDS_withExclusions_block6_V': MEPpp_FDS_withExclusions_block6_V,
    'relative_MEPpp_FDI_withExclusions_block6': relative_MEPpp_FDI_withExclusions_block6,
    'relative_MEPpp_FDS_withExclusions_block6': relative_MEPpp_FDS_withExclusions_block6,
    'sequence_block6': sequence_block6,
    'choice_block6': choice_block6,
    'result_block6': result_block6,
    'response_times_block6': response_times_block6,
}

# Create dataframe with variables side by side
df_summary = export_data.create_df_from_dict(variables_to_export_summary)

# Volunteer, Trial number (play_info) and Block id
play_info = np.arange(1, len(events_D4_block2) + len(events_D4_block4) + len(events_D4_block6) + 1)
vol_number = np.full(len(play_info), (int(volunteer_number[-2:])))
block_id_block2 = np.full(len(events_D4_block2), 2)
block_id_block4 = np.full(len(events_D4_block4), 4)
block_id_block6 = np.full(len(events_D4_block6), 6)
block_id = np.concatenate((block_id_block2, block_id_block4, block_id_block6))

# Stack variables to GKlab format - relative MEPs are with exclusions
rmsAmplitude_FDI_V = np.concatenate((rmsAmplitude_FDI_block2_V, rmsAmplitude_FDI_block4_V, rmsAmplitude_FDI_block6_V))
rmsAmplitude_FDS_V = np.concatenate((rmsAmplitude_FDS_block2_V, rmsAmplitude_FDS_block4_V, rmsAmplitude_FDS_block6_V))
MEPpp_FDI_V = np.concatenate((MEPpp_FDI_block2_V, MEPpp_FDI_block4_V, MEPpp_FDI_block6_V))
MEPpp_FDS_V = np.concatenate((MEPpp_FDS_block2_V, MEPpp_FDS_block4_V, MEPpp_FDS_block6_V))
relative_MEPpp_FDI = np.concatenate((relative_MEPpp_FDI_withExclusions_block2, relative_MEPpp_FDI_withExclusions_block4, relative_MEPpp_FDI_withExclusions_block6))
relative_MEPpp_FDS = np.concatenate((relative_MEPpp_FDS_withExclusions_block2, relative_MEPpp_FDS_withExclusions_block4, relative_MEPpp_FDS_withExclusions_block6))
sequence = np.concatenate((sequence_block2, sequence_block4, sequence_block6))
choice = np.concatenate((choice_block2, choice_block4, choice_block6))
result = np.concatenate((result_block2, result_block4, result_block6))
response_times = np.concatenate((response_times_block2, response_times_block4, response_times_block6))

# Gklab required columns
group_info = np.full(len(play_info), 1)
day_info = np.full(len(play_info), 1)
step_info = np.full(len(play_info), 1)
tree_info = np.full(len(play_info), 13)
ID_info = np.full(len(play_info),vol_number)

# Create dictionary with variables to export to GKlab
variables_to_export_gklab = {
    'group_info': group_info,
    'day_info': day_info,
    'play_info': play_info,
    'step_info': step_info,
    'tree_info': tree_info,
    'ID_info': ID_info,
    'response_time_info': response_times,
    'response_info': choice,
    'stochastic_chain_info': sequence,
    'relative_MEPpp_FDI': relative_MEPpp_FDI,
    'relative_MEPpp_FDS': relative_MEPpp_FDS,    
}

# Deal with NaN values filling with symbolic value
variables_to_export_gklab = utils.fill_missing_with_symbolic_value(variables_to_export_gklab)

# Create dataframe with variables side by side
df_gklab = export_data.create_df_from_dict(variables_to_export_gklab)

# Extract directory path and define CSV filenames
dir_path = os.path.dirname(fname)
csv_filename1 = 'df.csv'
csv_filename2 = 'df_gklab.csv'

# Combine the directory path with the filenames
csv_path1 = os.path.join(dir_path, csv_filename1)
csv_path2 = os.path.join(dir_path, csv_filename2)

# Export the DataFrames if export flag is True
if bool_export:
    export_data.export_to_csv(df_summary, csv_path1)
    export_data.export_to_GKlab_csv(df_gklab, csv_path2)
    

# ------------------------------------------------------------------
# MEP normalization by rest pulses
    
# # Get the event ID for "Display/D 4"
# d4_event_id = event_dict[np.str_('Display/D  4')]
# # Spliting Rest and Stim (in game) pulses
# D4_stim, D4_rest = signal_processing.split_d4_events(events_from_annot, 4) # usar events_D4?
