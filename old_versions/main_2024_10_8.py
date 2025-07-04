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
bool_plots = False   # Change to plot data
bool_exclude_familiarization = False # Change to remove 12 first trials
# normalization = 'mean_normalize'  # Choose between (rest_normalize, zscore, mean_normalize)

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
============================================
STEP 2 - Event Analysis
============================================
"""
# Split blocks and samples by annotations (D3)
(
    events_from_annot_B1, events_from_annot_B2, events_from_annot_B3, 
    events_from_annot_B4, events_from_annot_B5, events_from_annot_B6
) = split_events_into_blocks(
    events_from_annot, 
    event_id=3
)



# Extract events
events_from_annot_D1, _ = utils.extract_events_from_annotations(data_filtered, 'Display/D  1') # start trial
events_from_annot_D2, _ = utils.extract_events_from_annotations(data_filtered, 'Display/D  2') # arrows appearance
events_from_annot_G2, _ = utils.extract_events_from_annotations(data_filtered, 'Gkg/G  2') # left
events_from_annot_G4, _ = utils.extract_events_from_annotations(data_filtered, 'Gkg/G  4') # center
events_from_annot_G8, _ = utils.extract_events_from_annotations(data_filtered, 'Gkg/G  8') # right
events_from_annot_D4, event_dict_D4 = utils.extract_events_from_annotations(data_filtered, 'Display/D  4')

# Combine Gkg events
events_Gkg = utils.combine_gkg_events(events_from_annot_G2, events_from_annot_G4, events_from_annot_G8)

# Calculate response times
response_times, sequence, choice = signal_processing.calculate_response_times(
    events_from_annot_D2, events_Gkg, data_filtered)


# ----------------------------------
# Conversion of code names ('Gkg/G 2', 'Gkg/G 4' and 'Gkg/G 8') to alfabet numbers (0, 1 and 2)
alfabet = {
    'Gkg/G  2': 0,
    'Gkg/G  4': 1,
    'Gkg/G  8': 2
}
sequence = utils.convert_to_alfabet(sequence, alfabet)  # convert Gx1 (sequence) to alfabet numbers
choice = utils.convert_to_alfabet(choice, alfabet)  # convert Gx2 (choice) to alfabet numbers

# Analyse choices
result = signal_processing.analyze_choice(choice, sequence)

# Calculate elapsed time
elapsed_time = signal_processing.calculate_elapsed_time(events_from_annot_D1, data_filtered)

# Identify blocks of events
events_D1 = events_from_annot_D1[:, 0]
id_block = signal_processing.identify_blocks(events_D1)

# Get variables for blocks 2, 4 and 6
response_times_block_2_4_6, choice_block_2_4_6, sequence_block_2_4_6, result_block_2_4_6, \
elapsed_time_block_2_4_6, id_block_2_4_6 = utils.get_variables_blocks_2_4_6(
    response_times,
    choice,
    sequence,
    result,
    elapsed_time,
    id_block
)
  

"""
============================================
STEP 3 - MEP and RMS Analysis
============================================
"""
# Create the trigger array
trigger = signal_processing.create_trigger_array(data_filtered)

# Detect events 'Display/D 4' for Trigger
events_D4 = events_from_annot_D4[:, 0]

# Get the event ID for "Display/D 4"
d4_event_id = event_dict[np.str_('Display/D  4')]

# Spliting Rest and Stim (in game) pulses
D4_stim, D4_rest = signal_processing.split_d4_events(events_from_annot, 4) # usar events_D4?

# Remove D4 events during blocks without stimulus
D4_pulse_blocks, D4_rest_blocks = signal_processing.split_into_blocks(D4_stim)

# Get sampling frequency and set timing variables
sfreq = int(data_filtered.info["sfreq"])
time_before_stim = 0.01  # s
time_after_stim = 0.1  # s
time_before_rms = 0.5  # s

# Compute sample counts
samples_before_stim = int(time_before_stim * sfreq)
samples_after_stim = int(time_after_stim * sfreq)
samples_before_rms = int(time_before_rms * sfreq)

# Create figure for plotting
f, ax1, ax2 = plot_data.create_figure()

# Create x-axis (time) values
x = np.arange(-time_before_stim, time_after_stim, 1/sfreq)

# Process event windows for MEP and RMS
p2p_1, p2p_2, rmsAmplitude_FDI_V, rmsAmplitude_FDS_V = signal_processing.get_event_data_windows(
    data_filtered, D4_pulse_blocks, samples_before_stim, samples_after_stim, samples_before_rms
)

# Plot the extracted data
for i in range(len(D4_pulse_blocks)):
    win_1 = data_filtered._data[0][D4_pulse_blocks[i] - samples_before_stim : D4_pulse_blocks[i] + samples_after_stim]
    win_2 = data_filtered._data[1][D4_pulse_blocks[i] - samples_before_stim : D4_pulse_blocks[i] + samples_after_stim]
    plot_data.plot_emg_data(x, data_filtered, win_1, win_2, ax1, ax2)

# Configure and display the plot
if bool_plots:
    plot_data.configure_plot(data_filtered, ax1, ax2)

# Analyze amplitudes
rms_mean_FDI = np.mean(rmsAmplitude_FDI_V)
rms_mean_FDS = np.mean(rmsAmplitude_FDS_V)
rms_std_FDI = np.std(rmsAmplitude_FDI_V)
rms_std_FDS = np.std(rmsAmplitude_FDS_V)

# Set RMS thresholds for exclusion
rms_threshold_FDI = rms_mean_FDI + (2 * rms_std_FDI)
rms_threshold_FDS = rms_mean_FDS + (2 * rms_std_FDS)

# Store peak-to-peak amplitudes
MEPpp_FDI_V = p2p_1
MEPpp_FDS_V = p2p_2

"""
============================================
STEP 4 - Histogram Plots of Raw Signals
============================================
"""
# List of variables and names for histogram plotting
main_variables = [rmsAmplitude_FDI_V, rmsAmplitude_FDS_V, MEPpp_FDI_V, MEPpp_FDS_V]
variable_names = ['rms_FDI', 'rms_FDS', 'MEPpp_FDI_V', 'MEPpp_FDS_V']

# Plot histograms
if bool_plots:
    plot_data.plot_multiple_histograms(variable_names, main_variables)

"""
=================================================
STEP 5 - Analysis of RMS values and MEP Exclusion
=================================================
"""
# Get RMS time points
rms_time_points = data_filtered.times[D4_pulse_blocks]

# Plot RMS amplitudes
if bool_plots:
    plot_data.plot_rms_amplitudes(
        rms_time_points, rmsAmplitude_FDI_V, rmsAmplitude_FDS_V, rms_threshold_FDI, rms_threshold_FDS,
        data_filtered)

# Plot MEP amplitudes
if bool_plots:
    plot_data.plot_mep_amplitudes(
        rms_time_points, p2p_1, p2p_2, rmsAmplitude_FDI_V, rmsAmplitude_FDS_V, rms_threshold_FDI, 
        rms_threshold_FDS, data_filtered)

# Calculate relative MEP amplitudes without exclusion of MEPs by RMS
relative_MEPpp_FDI = signal_processing.calculate_relative_mep(p2p_1)
relative_MEPpp_FDS = signal_processing.calculate_relative_mep(p2p_2)

# Apply exclusion to MEP amplitudes based on RMS
p2p_1_excluded = signal_processing.exclude_mep_rms(p2p_1.copy(), rmsAmplitude_FDI_V, rms_threshold_FDI)
p2p_2_excluded = signal_processing.exclude_mep_rms(p2p_2.copy(), rmsAmplitude_FDS_V, rms_threshold_FDS)

# Calculate relative MEP amplitudes after exclusion of MEPs by RMS
relative_MEPpp_FDI_withExclusions = signal_processing.calculate_relative_mep(p2p_1_excluded)
relative_MEPpp_FDS_withExclusions = signal_processing.calculate_relative_mep(p2p_2_excluded)

# Plot MEP vs RMS amplitudes (with and without exclusion)
if bool_plots:
    plot_data.plot_mep_vs_rms(rmsAmplitude_FDI_V, rmsAmplitude_FDS_V, p2p_1, p2p_2)

# Indices where MEPs were excluded
excluded_indices_ch1 = np.where(~np.isnan(p2p_1_excluded))[0]
excluded_indices_ch2 = np.where(~np.isnan(p2p_2_excluded))[0]

# Plot MEP vs RMS for excluded data
if bool_plots:
    plot_data.plot_excluded_mep_vs_rms(
        rmsAmplitude_FDI_V, rmsAmplitude_FDS_V, p2p_1_excluded, p2p_2_excluded, excluded_indices_ch1,
        excluded_indices_ch2)

"""
============================================
STEP 6 - Data Handling for Exportation
============================================
"""
# Trial number
trial_numbers = np.arange(1, len(events_from_annot_D4) + 1)

# ------------------------------------------------------------------
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