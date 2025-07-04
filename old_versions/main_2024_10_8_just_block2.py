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
volunteer_number = 'V01'  # Change volunteer number for analysis
bool_export = False  # Change to export data to CSV
bool_plots = True   # Change to plot data
bool_exclude_familiarization = False # Change to remove 12 first trials
# normalization = 'mean_normalize'  # Choose between (rest_normalize, zscore, mean_normalize)
rms_thresh = 2     # in standard deviations. Used for both FDI and FDS exclusion criteria


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
if bool_plots:
    plot_data.plot_spectrum_amplitude(raw, channel_index=0, fmin=1, fmax=600)
    plot_data.plot_psd(raw)

## Notch filtering and ploting
raw_notch = signal_processing.notch_filter_data(raw)
if bool_plots:
    plot_data.plot_spectrum_amplitude(raw_notch, channel_index=0, fmin=1, fmax=600)
    plot_data.plot_psd(raw_notch)

## Bandpass filtering
bandpass_filter = signal_processing.apply_bandpass_filter(raw_notch, l_freq=20, h_freq=500)
data_filtered = signal_processing.create_filtered_raw_object(bandpass_filter, raw_notch.info)
if bool_plots:
    plot_data.plot_spectrum_amplitude(data_filtered, channel_index=0, fmin=1, fmax=600)
    plot_data.plot_psd(data_filtered)

# Add annotations from the original raw data and plot filtered data
data_filtered = utils.add_annotations_to_filtered(data_filtered, raw_notch)
if bool_plots:
    data_filtered.plot()

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
    events_from_annot_B1, events_from_annot_B2, events_from_annot_B3, 
    events_from_annot_B4, events_from_annot_B5, events_from_annot_B6
) = signal_processing.split_events_into_blocks(
    events_from_annot, 
    event_id=3
)

# Plot to verify event blocks
if bool_plots:
    event_blocks = [
        events_from_annot_B1,
        events_from_annot_B2,
        events_from_annot_B3,
        events_from_annot_B4,
        events_from_annot_B5,
        events_from_annot_B6
    ]
    plot_data.plot_event_blocks(event_blocks, sfreq=data_filtered.info['sfreq'])

# Create the trigger array
trigger = signal_processing.create_trigger_array(data_filtered)

# Get sampling frequency and set timing variables
sfreq = int(data_filtered.info["sfreq"])
time_before_stim = 0.01  # s
time_after_stim = 0.1  # s
time_before_rms = 0.5  # s

# Compute sample counts
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
events_from_annot_D1_block2 = utils.extract_events_from_annot(events_from_annot_B2, 3)
events_from_annot_D2_block2 = utils.extract_events_from_annot(events_from_annot_B2, 2)
events_from_annot_G2_block2 = utils.extract_events_from_annot(events_from_annot_B2, 6)
events_from_annot_G4_block2 = utils.extract_events_from_annot(events_from_annot_B2, 7)
events_from_annot_G8_block2 = utils.extract_events_from_annot(events_from_annot_B2, 8)
events_from_annot_D4_block2 = utils.extract_events_from_annot(events_from_annot_B2, 4)

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
STEP 3 - MEP and RMS Analysis for Block 2
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

# Calculate relative MEP amplitudes without exclusion of MEPs by RMS
relative_MEPpp_FDI_block2 = signal_processing.calculate_relative_mep(MEPpp_FDI_block2_V)
relative_MEPpp_FDS_block2 = signal_processing.calculate_relative_mep(MEPpp_FDS_block2_V)

# Apply exclusion to MEP amplitudes based on RMS
MEP_FDI_excluded_block2 = signal_processing.exclude_mep_rms(MEPpp_FDI_block2_V.copy(), rmsAmplitude_FDI_block2_V, rms_threshold_FDI)
MEP_FDS_excluded_block2 = signal_processing.exclude_mep_rms(MEPpp_FDS_block2_V.copy(), rmsAmplitude_FDS_block2_V, rms_threshold_FDS)

# Calculate relative MEP amplitudes after exclusion of MEPs by RMS
relative_MEPpp_FDI_withExclusions_block2 = signal_processing.calculate_relative_mep(MEP_FDI_excluded_block2)
relative_MEPpp_FDS_withExclusions_block2 = signal_processing.calculate_relative_mep(MEP_FDS_excluded_block2)

# Plot MEP vs RMS amplitudes (with and without exclusion)
if bool_plots:
    plot_data.plot_mep_vs_rms(rmsAmplitude_FDI_block2_V, rmsAmplitude_FDS_block2_V, MEPpp_FDI_block2_V, MEPpp_FDS_block2_V)

# Indices where MEPs were excluded
excluded_indices_FDI_block2 = np.where(~np.isnan(MEP_FDI_excluded_block2))[0]
excluded_indices_FDS_block2 = np.where(~np.isnan(MEP_FDS_excluded_block2))[0]

# Plot MEP vs RMS for excluded data
if bool_plots:
    plot_data.plot_excluded_mep_vs_rms(
        rmsAmplitude_FDI_block2_V, rmsAmplitude_FDS_block2_V, MEP_FDI_excluded_block2, MEP_FDS_excluded_block2, excluded_indices_FDI_block2,
        excluded_indices_FDS_block2)




































































"""
============================================
STEP 4 - Plots of Raw Signals
============================================
"""
# List of variables and names for histogram plotting
main_variables = [rmsAmplitude_FDI_V, rmsAmplitude_FDS_V, MEPpp_FDI_V, MEPpp_FDS_V]
variable_names = ['rms_FDI', 'rms_FDS', 'MEPpp_FDI_V', 'MEPpp_FDS_V']

# Plot histograms
if bool_plots:
    plot_data.plot_multiple_histograms(variable_names, main_variables)

# Criar novamente scatter para os 3 blocos juntos como tínhamos antes

"""
============================================
STEP 6 - Data Handling for Exportation
============================================
"""
# Trial number
trial_numbers = np.arange(1, len(events_from_annot_D4) + 1)

# ------------------------------------------------------------------
# Criar data frames separados por blocos e depois juntá-los em 1




# Prepare summary dataframe
df_summary = export_data.create_df_summary(
    rmsAmplitude_FDI_V, rmsAmplitude_FDS_V, MEPpp_FDI_V, MEPpp_FDS_V, 
    relative_MEPpp_FDI, relative_MEPpp_FDS, relative_MEPpp_FDI_withExclusions,
    relative_MEPpp_FDS_withExclusions, sequence, choice, result, response_times,
    elapsed_time, id_block)

# Prepare GKlab dataframe (verificar estrutura)
df_GKlab = export_data.create_GKlab_df(
    rmsAmplitude_FDI_V, rmsAmplitude_FDS_V, MEPpp_FDI_V, MEPpp_FDS_V, sequence,
    choice, result, response_times, elapsed_time)

# ------------------------------------------------------------------

# Extract directory path and define CSV filenames
dir_path = os.path.dirname(fname)
csv_filename1 = 'df.csv'
csv_filename2 = 'df_GKlab.csv'

# Combine the directory path with the filenames
csv_path1 = os.path.join(dir_path, csv_filename1)
csv_path2 = os.path.join(dir_path, csv_filename2)

# Exclude familiarization trials
if bool_exclude_familiarization:
    df_summary = df_summary.tail(-12)
    df_GKlab = df_GKlab.tail(-12)

# Export the DataFrames if export flag is True
if bool_export:
    export_data.export_to_csv(df_summary, csv_path1)
    export_data.export_to_GKlab_csv(df_GKlab, csv_path2)
    

# ------------------------------------------------------------------
# MEP normalization by rest pulses
    
# # Get the event ID for "Display/D 4"
# d4_event_id = event_dict[np.str_('Display/D  4')]
# # Spliting Rest and Stim (in game) pulses
# D4_stim, D4_rest = signal_processing.split_d4_events(events_from_annot, 4) # usar events_D4?
