"""
=================================================
Main Processing Script
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
volunteer_number = 'V15'         # Change volunteer number for analysis
bool_export = True               # Change to export data to CSV
bool_plots = False               # Change to plot data
exclusion_method = 'RMS'         # Choose between (outliers or RMS)
rms_thresh = 2                   # in standard deviations. Used for both FDI and FDS exclusion criteria when exclusion_method = 'RMS'

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
if bool_plots:
    data_filtered.plot()

## Verify markers
utils.marker_verification(raw, data_filtered)
events_from_annot, event_dict = mne.events_from_annotations(data_filtered)

# Find the index of the 1st D4 and slice the array
start_index = np.argmax(events_from_annot[:, 2] == 4)
events_from_annot = events_from_annot[start_index:]

# Split events into InGame and OutGame
events_from_annot_outGame, events_from_annot = signal_processing.split_events_InOut_game(events_from_annot)

# To fix non-rest markers
if volunteer_number == 'V03':
    # Time of rest markers - modify as needed
    marker_times_sec = [1515.116, 1522.372, 1529.543, 1536.354, 1541.368, 1546.996, 1552.275, 1559.171,
                        3471.092, 3481.055, 3486.988, 3491.317, 3499.317, 3504.706, 3508.994, 3517.172,
                        5462.303, 5468.657, 5474.451, 5479.522, 5484.997, 5490.405, 5495.878, 5501.008]

    # Convert times in samples
    sfreq = int(data_filtered.info["sfreq"])
    marker_rest_samples = [int(x * sfreq) for x in marker_times_sec]

    # Create an array with 3 columns and marker_rest_samples as the first column
    events_from_annot_outGame = np.array([marker_rest_samples, [0] * len(marker_rest_samples), [0] * len(marker_rest_samples)]).T

# To view annotations
# if bool_plots:
#     mne.viz.plot_events(events_from_annot, sfreq=data_filtered.info['sfreq'], event_id=event_dict)

"""
====================================================
STEP 2 - Seting General Parameters
====================================================
"""
# Create the trigger array
trigger = signal_processing.create_trigger_array(data_filtered)

# Get sampling frequency and set timing variables
sfreq = int(data_filtered.info["sfreq"])
time_before_stim = 0.01  # s
time_after_stim = 0.06  # s
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
STEP 3 - Event Analysis
============================================
"""
# Extract events from annotations based on event_id
events_from_annot_D1 = utils.extract_events_from_annot(events_from_annot, 1)
events_from_annot_D2 = utils.extract_events_from_annot(events_from_annot, 2)
events_from_annot_G2 = utils.extract_events_from_annot(events_from_annot, 6)
events_from_annot_G4 = utils.extract_events_from_annot(events_from_annot, 7)
events_from_annot_G8 = utils.extract_events_from_annot(events_from_annot, 8)
events_from_annot_D4 = utils.extract_events_from_annot(events_from_annot, 4)

# Combine Gkg events G2, G4 and G8
events_Gkg = utils.combine_gkg_events(events_from_annot_G2, events_from_annot_G4, events_from_annot_G8)

# Calculate response times - Using D2 marker (arrows appearance)
response_times, sequence, choice = signal_processing.calculate_response_times(
    events_from_annot_D2, events_Gkg, data_filtered)

# Get sequence and choice
sequence = utils.convert_to_alfabet(sequence, alfabet)  # convert Gx1 (sequence) to alfabet numbers
choice = utils.convert_to_alfabet(choice, alfabet)      # convert Gx2 (choice) to alfabet numbers

# Analyse choices
result = signal_processing.analyze_choice(choice, sequence)

# Get D4 out game events
events_D4_outGame = events_from_annot_outGame[:, 0]

# Process event windows and get MEP out game
MEPpp_FDI_outGame_V, MEPpp_FDS_outGame_V, _, _ = signal_processing.get_event_data_windows(
    data_filtered, events_D4_outGame, samples_before_stim, samples_after_stim, samples_before_rms
)

"""
=============================
STEP 4 - MEP and RMS Analysis
=============================
"""
# Detect events 'Display/D 4' for Trigger
events_D4 = events_from_annot_D4[:, 0]

# To cut an extra D4 marker in V03
if volunteer_number == 'V03':
    events_D4 = events_D4[events_D4 != 3691471]

# Create figure for plotting
f, ax1, ax2 = plot_data.create_figure("Raw MEP amplitudes")

# Create x-axis (time) values
x = np.arange(-time_before_stim, time_after_stim, 1/sfreq)

# Process event windows and get MEP and RMS
MEPpp_FDI_V, MEPpp_FDS_V, rmsAmplitude_FDI_V, rmsAmplitude_FDS_V = signal_processing.get_event_data_windows(
    data_filtered, events_D4, samples_before_stim, samples_after_stim, samples_before_rms
)

# Plot the extracted data
for i in range(len(events_D4)):
    win_1 = data_filtered._data[0][events_D4[i] - samples_before_stim : events_D4[i] + samples_after_stim]
    win_2 = data_filtered._data[1][events_D4[i] - samples_before_stim : events_D4[i] + samples_after_stim]
    plot_data.plot_emg_data(x, data_filtered, win_1, win_2, ax1, ax2)

# Configure and display the plot of MEPs overlayed for FDI and FDS
if bool_plots:
    plot_data.configure_plot(data_filtered, ax1, ax2)

# Correction valid for V09 because of invalid MEPs
if volunteer_number == 'V09':
    MEPpp_FDI_V[MEPpp_FDI_V < (60 / 1000000)] = np.nan
    MEPpp_FDS_V[MEPpp_FDS_V < (100 / 1000000)] = np.nan
    
"""
============================================
STEP 5 - Required Data for Gklab
============================================
"""
## Gklab required columns
play_info = np.arange(1, len(response_times) + 1)
vol_number = np.full(len(play_info), (int(volunteer_number[-2:])))
group_info = np.full(len(play_info), 1)
day_info = np.full(len(play_info), 1)
step_info = np.full(len(play_info), 1)
tree_info = np.full(len(play_info), 13)
ID_info = np.full(len(play_info),vol_number)
relMean_MEPpp_FDI = np.full(len(play_info), 0)
relMean_MEPpp_FDS = np.full(len(play_info), 0)
block_info = np.concatenate((
    np.full(11, 0),   
    np.full(199, 1),    
    np.full(199, 2),            
    np.full(199, 3),            
    np.full(199, 4),            
    np.full(199, 5),
    np.full(199, 6)             
))

"""
=================================================
STEP 6 - MEP normalization and Outliers exclusion
=================================================
"""
if exclusion_method == 'RMS':
    # Analyze RMS amplitudes
    rms_mean_FDI = np.mean(rmsAmplitude_FDI_V)
    rms_mean_FDS = np.mean(rmsAmplitude_FDS_V)
    rms_std_FDI = np.std(rmsAmplitude_FDI_V)
    rms_std_FDS = np.std(rmsAmplitude_FDS_V)

    # Set RMS thresholds for exclusion
    rms_threshold_FDI = rms_mean_FDI + (rms_thresh * rms_std_FDI)
    rms_threshold_FDS = rms_mean_FDS + (rms_thresh * rms_std_FDS)    
    
    # Get RMS time points
    rms_time_points = data_filtered.times[events_D4]

    # Plot RMS amplitudes over time
    if bool_plots:
        plot_data.plot_rms_amplitudes(
            rms_time_points, rmsAmplitude_FDI_V, rmsAmplitude_FDS_V, rms_threshold_FDI, rms_threshold_FDS,
            data_filtered)

    # Plot MEP amplitudes over time
    if bool_plots:
        plot_data.plot_mep_amplitudes(
            rms_time_points, MEPpp_FDI_V, MEPpp_FDS_V, rmsAmplitude_FDI_V, rmsAmplitude_FDS_V, rms_threshold_FDI, 
            rms_threshold_FDS, data_filtered)
        
    # Apply exclusion to MEP amplitudes based on RMS (gives NaN if excluded)
    MEPpp_FDI_withExclusions_V = signal_processing.exclude_mep_rms(MEPpp_FDI_V.copy(), rmsAmplitude_FDI_V, rms_threshold_FDI)
    MEPpp_FDS_withExclusions_V = signal_processing.exclude_mep_rms(MEPpp_FDS_V.copy(), rmsAmplitude_FDS_V, rms_threshold_FDS)

if exclusion_method == 'outliers':     
    # Apply exclusion based on IQR (return NaN if excluded)
    MEPpp_FDI_withExclusions_V = signal_processing.remove_outliers_by_index(MEPpp_FDI_V, block_info)
    MEPpp_FDS_withExclusions_V = signal_processing.remove_outliers_by_index(MEPpp_FDS_V, block_info)

# Convert from V to mV
MEPpp_FDI_withExclusions_µV = MEPpp_FDI_withExclusions_V * 1e6
MEPpp_FDS_withExclusions_µV = MEPpp_FDS_withExclusions_V * 1e6
MEPpp_FDI_outGame_µV = MEPpp_FDI_outGame_V * 1e6
MEPpp_FDS_outGame_µV = MEPpp_FDS_outGame_V * 1e6

# Mean of MEPs out game
MEP_mean_FDI_outGame_µV = np.mean(MEPpp_FDI_outGame_µV)
MEP_mean_FDS_outGame_µV = np.mean(MEPpp_FDS_outGame_µV)

# Array of MEP Mean out game to be included on data frame
FDImep_outGame = np.full(len(play_info), MEP_mean_FDI_outGame_µV)
FDSmep_outGame = np.full(len(play_info), MEP_mean_FDS_outGame_µV)

# MEP normalization by rest
relRest_MEPpp_FDI = MEPpp_FDI_withExclusions_µV / MEP_mean_FDI_outGame_µV
relRest_MEPpp_FDS = MEPpp_FDS_withExclusions_µV / MEP_mean_FDS_outGame_µV

# MEP normalization by mean
relMean_MEPpp_FDI = signal_processing.normalize_mep_by_mean(MEPpp_FDI_withExclusions_µV, block_info)
relMean_MEPpp_FDS = signal_processing.normalize_mep_by_mean(MEPpp_FDS_withExclusions_µV, block_info)

"""
============================================
STEP 7 - Data Handling for Exportation
============================================
"""
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
    'MEPpp_FDI_µV': MEPpp_FDI_withExclusions_µV,
    'MEPpp_FDS_µV': MEPpp_FDS_withExclusions_µV,
    'relRest_MEPpp_FDI': relRest_MEPpp_FDI,
    'relRest_MEPpp_FDS': relRest_MEPpp_FDS,
    'relMean_MEPpp_FDI': relMean_MEPpp_FDI,
    'relMean_MEPpp_FDS': relMean_MEPpp_FDS,
    'block_info': block_info,
    'FDImep_outGame': FDImep_outGame,
    'FDSmep_outGame': FDSmep_outGame   
}                                   

# # Deal with NaN values filling with symbolic value (receive 99999)
variables_to_export_gklab = utils.fill_missing_with_symbolic_value(variables_to_export_gklab)

# # Create dataframe with variables side by side
df_gklab = export_data.create_df_from_dict(variables_to_export_gklab)

# Extract directory path and define CSV filenames
dir_path = os.path.dirname(fname)
csv_filename = 'df_' + volunteer_number + '_gklab.csv'

# Combine the directory path with the filenames
csv_path = os.path.join(dir_path, csv_filename)

# Export the DataFrames if export flag is True
if bool_export:
    export_data.export_to_GKlab_csv(df_gklab, csv_path)