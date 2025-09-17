"""
=================================================
Plot Script for Visualizations
=================================================
"""
import matplotlib.pyplot as plt
import numpy as np
import mne
from scipy.stats import linregress
import seaborn as sns
import pandas as pd

def plot_psd(data, fmax=600):
    """Plot Power Spectral Density (PSD) of the data."""
    data.compute_psd(fmax=fmax).plot(average=True, picks="data", exclude="bads")
    plt.show()
    

# Fix names of the channel plots
def plot_spectrum_amplitude(signal, start_time=0.0, stop_time=None, channel_index=0, fmin=0.0, fmax=100.0):
    """
    Plots the spectrum amplitude of the EEG signal from a specified channel.

    Parameters:
    - raw: MNE Raw object containing the EEG data.
    - start_time: Start time in seconds for the analysis window. Defaults to 0.0 seconds.
    - stop_time: Stop time in seconds for the analysis window. If None, uses the entire signal.
    - channel_index: Index of the channel to analyze. Defaults to the first channel (0).
    - fmin: Minimum frequency for the spectrum plot. Defaults to 0.0 Hz.
    - fmax: Maximum frequency for the spectrum plot. Defaults to 100.0 Hz.

    Returns:
    - None. Displays the spectrum amplitude plot. 
    """
    # If stop_time is None, use the total duration of the recording
    if stop_time is None:
        stop_time = signal.times[-1]  # Total duration in seconds    
    
    # Extract data from the Raw object
    data, times = signal[channel_index, int(start_time * signal.info['sfreq']):int(stop_time * signal.info['sfreq'])]

    # Perform Fourier Transform to get the frequency domain representation
    n_samples = len(data[0])
    freqs = np.fft.rfftfreq(n_samples, 1.0 / signal.info['sfreq'])
    fft_data = np.fft.rfft(data[0])
    
    # Compute the amplitude spectrum
    amplitude_spectrum = np.abs(fft_data)
    
    # Select frequency range for plotting
    freq_mask = (freqs >= fmin) & (freqs <= fmax)
    
    # Plot the spectrum amplitude
    plt.figure(figsize=(10, 6))
    plt.plot(freqs[freq_mask], amplitude_spectrum[freq_mask], label=f'Channel {channel_index}')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude')
    plt.title(f'Spectrum Amplitude (Channel {channel_index})')
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_emg_data(x, data_filtered, win_1, win_2, ax1, ax2):
    """Plot EMG data on two axes."""
    ax1.plot(x * 1000, win_1 * 1e6, color="gray", alpha=0.08)
    ax2.plot(x * 1000, win_2 * 1e6, color="gray", alpha=0.08)

def configure_plot(data_filtered, ax1, ax2):
    """Configure plot labels, titles, and axes."""
    ax1.axvline(x=0, color='k', linestyle='--')
    ax2.axvline(x=0, color='k', linestyle='--')
    ax1.set_title(f"EMG {data_filtered.ch_names[0]}")
    ax2.set_title(f"EMG {data_filtered.ch_names[1]}")
    ax1.set_xlabel('Time [ms]')
    ax1.set_ylabel('Voltage [uV]')
    ax2.set_xlabel('Time [ms]')
    ax2.set_ylabel('Voltage [uV]')
    plt.show()

def create_figure(window_title):
    """Create a figure with two subplots."""
    f, (ax1, ax2) = plt.subplots(1, 2)
    f.canvas.manager.set_window_title(window_title)
    return f, ax1, ax2


def plot_rms_amplitudes(rms_time_points, rms_1, rms_2, rms_threshold_ch1, rms_threshold_ch2, data_filtered):
    f, (ax1, ax2) = plt.subplots(1, 2)
    f.canvas.manager.set_window_title("Figure 7")

    excluded_rms_1 = np.where((rms_1 > rms_threshold_ch1), rms_1 * 1e6, np.nan)
    ax1.plot(rms_time_points, rms_1 * 1e6, marker='o', linestyle='None', label='Included RMS')
    ax1.plot(rms_time_points, excluded_rms_1, 'ro', label='Excluded RMS', alpha=0.5)

    excluded_rms_2 = np.where((rms_2 > rms_threshold_ch2), rms_2 * 1e6, np.nan)
    ax2.plot(rms_time_points, rms_2 * 1e6, marker='o', linestyle='None', label='Included RMS')
    ax2.plot(rms_time_points, excluded_rms_2, 'ro', label='Excluded RMS', alpha=0.5)

    ax1.set_title(f"RMS Amplitude {data_filtered.ch_names[0]}")
    ax2.set_title(f"RMS Amplitude {data_filtered.ch_names[1]}")
    ax1.set_xlabel('Time [s]')
    ax1.set_ylabel('RMS Amplitude')
    ax2.set_xlabel('Time [s]')
    ax2.set_ylabel('RMS Amplitude')
    ax1.legend()
    ax2.legend()
    plt.show()

def plot_mep_amplitudes(rms_time_points, p2p_1, p2p_2, rms_1, rms_2, rms_threshold_ch1, rms_threshold_ch2, data_filtered):
    f, (ax1, ax2) = plt.subplots(1, 2)
    f.canvas.manager.set_window_title("Figure 8")

    excluded_mep_1 = np.where((rms_1 > rms_threshold_ch1), p2p_1 * 1e6, np.nan)
    ax1.plot(rms_time_points, p2p_1 * 1e6, marker='o', linestyle='None', label='Included MEP')
    ax1.plot(rms_time_points, excluded_mep_1, 'ro', label='Excluded MEP', alpha=0.5)

    excluded_mep_2 = np.where((rms_2 > rms_threshold_ch2), p2p_2 * 1e6, np.nan)
    ax2.plot(rms_time_points, p2p_2 * 1e6, marker='o', linestyle='None', label='Included MEP')
    ax2.plot(rms_time_points, excluded_mep_2, 'ro', label='Excluded MEP', alpha=0.5)

    ax1.set_title(f"MEP Amplitude {data_filtered.ch_names[0]}")
    ax1.set_xlabel('Time [s]')
    ax1.set_ylabel('Voltage [µV]')
    ax1.legend()

    ax2.set_title(f"MEP Amplitude {data_filtered.ch_names[1]}")
    ax2.set_xlabel('Time [s]')
    ax2.set_ylabel('Voltage [µV]')
    ax2.legend()

    plt.show()

def plot_success_rate_individual(success_rates, labels, colors=None, std_devs=None):
    """
    Create a bar plot to compare multiple success rates and add value labels on the bars.

    Parameters:
    success_rates (list of float): List of success rates to be plotted.
    labels (list of str): List of labels corresponding to each success rate.
    colors (list of str, optional): List of colors for each bar. Defaults to a preset color scheme.
    std_devs (list of float, optional): List of standard deviations for each success rate. 
                                         If provided, error bars will be included in the plot.
    """
       
    # Use default colors if none are provided
    if colors is None:
        colors = plt.cm.tab20.colors[:len(success_rates)]  # Use a colormap with enough variety
    
    # Create a figure with specified size and resolution
    plt.figure(figsize=(10, 6), dpi=600)  # Adjust figsize and dpi as needed
    
    # Create the bar plot with error bars if std_devs are provided
    bars = plt.bar(labels, success_rates, color=colors, yerr=std_devs, capsize=5, width=0.8)
    
    # Add titles and labels with increased font sizes
    plt.title('Comparison of Success Rates', fontsize=16)
    plt.ylabel('Success Rate', fontsize=16)
    
    # Set y-axis limits from 0 to 1 for better visualization
    plt.ylim(0, 1)
    
    # Adding value labels on top of each bar with increased font size
    for bar in bars:
        yval = bar.get_height()  # Get the height of each bar
        plt.text(bar.get_x() + bar.get_width() / 2, yval, f'{yval:.2f}', ha='center', va='bottom', fontsize=12)

    # Increase font size for tick labels
    plt.xticks(fontsize=14)  # X-axis tick labels
    plt.yticks(fontsize=14)  # Y-axis tick labels
    
    # Remove left and upper spines
    ax = plt.gca()  # Get current axes
    ax.spines['right'].set_visible(False)  # Remove left spine
    ax.spines['top'].set_visible(False)   # Remove top spine

    # Show the plot
    plt.show()
    

def plot_success_rate_comparison_group(list1, list2, labels):
    """
    Create boxplots for two paired lists of success rates and overlay individual data points.

    Parameters:
    list1 (list of float): The first list of success rates.
    list2 (list of float): The second list of success rates.
    labels (list of str): List containing labels for the two boxplots.
    """
    # Check if the number of labels matches the number of lists
    if len(labels) != 2:
        raise ValueError("Please provide exactly two labels for the two lists.")

    # Prepare the data for Seaborn
    data = {
        'Category': [labels[0]] * len(list1) + [labels[1]] * len(list2),
        'Success Rate': list1 + list2
    }
    
    df = pd.DataFrame(data)

    # Create a figure with specified size and resolution
    plt.figure(figsize=(10, 6), dpi=600)

    # Create a color palette with unique colors for each pair
    unique_colors = sns.color_palette("hsv", len(list1))  # Using HSV palette for distinct colors

    # Plot the boxplot using hue for categories
    ax = sns.boxplot(x='Category', y='Success Rate', data=df, palette='pastel', hue='Category', showmeans=True, legend=False)

    # Overlay the strip plot with paired colors for each point
    for i in range(len(list1)):
        plt.scatter(labels[0], list1[i], color=unique_colors[i], alpha=0.7, edgecolor='black', s=50)
        plt.scatter(labels[1], list2[i], color=unique_colors[i], alpha=0.7, edgecolor='black', s=50)

    # Set transparency for the boxplot faces
    for patch in ax.patches:  # ax.artists can also be used depending on your version of Seaborn
        r, g, b, _ = patch.get_facecolor()  # Get current face color (RGBA)
        patch.set_facecolor((r, g, b, 0.3))  # Set new face color with transparency

    # Add titles and labels with increased font sizes
    plt.title(' ', fontsize=16)
    plt.ylabel('Taxa de acerto', fontsize=16)

    # Set y-axis limits from 0 to 1 for better visualization
    plt.ylim(0.6, 0.9)

    # Increase font size for tick labels
    plt.xticks(fontsize=14)  # X-axis tick labels
    plt.yticks(fontsize=14)  # Y-axis tick labels

    # Create a legend with positional entries (Vx: value1 / value2)
    handles = [
        plt.Line2D(
            [0], [0], 
            marker='o', 
            color='w', 
            label=f'V{i + 1}: {list1[i]:.2f} / {list2[i]:.2f}', 
            markerfacecolor=unique_colors[i]
        ) 
        for i in range(len(list1))
    ]
    
    plt.legend(handles=handles, title="TA: 1200 / 1000", bbox_to_anchor=(1.05, 1), loc='upper left')

    # Remove left and upper spines
    ax.spines['right'].set_visible(False)  # Remove right spine
    ax.spines['top'].set_visible(False)   # Remove top spine

    # Show the plot
    plt.tight_layout()
    plt.show()   
    
def plot_success_rates_by_blocks_group(df):
    """
    Create boxplots showing success rates for each block, with data grouped by volunteers (ID_info).

    Parameters:
    df (pd.DataFrame): A DataFrame containing 'ID_info', 'block_info', 'response_info', and 'stochastic_chain_info'.
    """
    # Calculate success rates by ID and block
    results = {}

    # Group by 'ID_info'
    for id_value, group in df.groupby('ID_info'):
        # For each ID, calculate success rates for each block
        success_rates = group.groupby('block_info').apply(
            lambda block: (block['response_info'] == block['stochastic_chain_info']).mean()
        ).to_dict()
        
        # Store the results in the dictionary
        results[id_value] = success_rates

    # Prepare data for plotting
    plot_data = []
    
    for id_value, blocks in results.items():
        for block, rate in blocks.items():
            plot_data.append({'ID_info': id_value, 'block_info': block, 'success_rate': rate})

    # Create a DataFrame from the prepared data
    plot_df = pd.DataFrame(plot_data)

    # Define colors for volunteers (dots)
    unique_volunteer_colors = sns.color_palette("husl", len(plot_df['ID_info'].unique()))
    volunteer_color_map = {id_value: unique_volunteer_colors[i] for i, id_value in enumerate(plot_df['ID_info'].unique())}

    # Create boxplots with hue assignment
    plt.figure(figsize=(10, 6), dpi=900)
    ax = sns.boxplot(x='block_info', y='success_rate', data=plot_df, hue='block_info', palette='pastel', showmeans=True, dodge=False)

    # Set transparency for the boxplot faces
    for patch in ax.patches:
        r, g, b, _ = patch.get_facecolor()  # Get current face color (RGBA)
        patch.set_facecolor((r, g, b, 0.3))  # Set new face color with transparency

    # Overlay the volunteer dots with corresponding colors
    handles = []  # List to store legend handles
    added_volunteers = set()  # To avoid duplicate legend entries
    
    # Get x-axis positions of each boxplot category
    x_positions = {category: i for i, category in enumerate(sorted(plot_df['block_info'].unique()))}

    for _, row in plot_df.iterrows():
        dot_color = volunteer_color_map[row['ID_info']]  # Assign a unique color to each volunteer
        plt.scatter(x=x_positions[row['block_info']], y=row['success_rate'], 
                    color=dot_color, alpha=0.7, edgecolor='black', s=50)

        # Add to legend if not already added
        if row['ID_info'] not in added_volunteers:
            handles.append(plt.Line2D([0], [0], marker='o', color='w', label=f'V{int(row["ID_info"])}', 
                                       markerfacecolor=dot_color))
            added_volunteers.add(row['ID_info'])

    # Calculate mean success rates for each block to draw the dashed line
    mean_success_rates = plot_df.groupby('block_info')['success_rate'].mean()

    # Map mean success rates to their corresponding x positions
    mean_x_positions = [x_positions[block] for block in mean_success_rates.index]

    # Plot dashed line connecting mean values at correct x positions
    plt.plot(mean_x_positions, mean_success_rates.values,
             linestyle='--', color='gray', linewidth=1)

    # Add titles and labels
    plt.title(' ', fontsize=16)
    plt.xlabel('Block', fontsize=14)
    plt.ylabel('Success Rate', fontsize=14)
    
    # Set y-axis limits from 0 to 1 for better visualization
    plt.ylim(0.3, 1)

    # Increase font size for tick labels
    plt.xticks(fontsize=12)  # X-axis tick labels
    plt.yticks(fontsize=12)  # Y-axis tick labels

    # Create a legend with unique entries for volunteers
    plt.legend(handles=handles, title="Volunteer", bbox_to_anchor=(1.05, 1), loc='upper left')

    # Remove right and upper spines
    ax.spines['right'].set_visible(False)  # Remove right spine
    ax.spines['top'].set_visible(False)   # Remove top spine

    # Show the plot
    plt.tight_layout()
    plt.show()

def plot_means_boxplot(data):
    """
    Create a boxplot to visualize mean values from a nested dictionary.

    Parameters:
    data (dict): A nested dictionary with keys 'mean_NoPulse' and 'mean_Pulse'.
    """
    # Prepare data for plotting
    plot_data = {
        'Group': [],
        'Mean Value': []
    }

    # Iterate through the nested dictionary and populate plot_data
    for key, values in data.items():
        plot_data['Group'].append('mean_NoPulse')
        plot_data['Mean Value'].append(values['mean_NoPulse'])

        plot_data['Group'].append('mean_Pulse')
        plot_data['Mean Value'].append(values['mean_Pulse'])

    # Create a DataFrame from the prepared data
    df = pd.DataFrame(plot_data)

    # Create boxplot with light colors using hue correctly
    plt.figure(figsize=(10, 6), dpi=600)
    sns.boxplot(x='Group', y='Mean Value', data=df, hue='Group', 
                palette={'mean_NoPulse': '#ADD8E6', 'mean_Pulse': '#FFB6C1'}, 
                dodge=False, legend=False)

    # Add titles and labels
    plt.title(' ', fontsize=16)
    plt.xlabel(' ', fontsize=14)
    plt.ylabel('Taxa de acerto', fontsize=14)

    # Remove spines
    ax = plt.gca()  # Get current axes
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    # Set y-axis limits if provided
    plt.ylim(0.5, 0.9)

    # Show the plot
    plt.tight_layout()
    plt.show()


    

def plot_boxplot(df, value_column, group_column, title='Boxplot', xlabel='Groups', ylabel='Values',
                 figsize=(14, 10), title_fontsize=16, label_fontsize=14, tick_fontsize=12, dpi=100,
                 outlier_threshold=None, group_values=None):
    """
    Create a boxplot for a specified value column, grouped by another column.

    Parameters:
    df (DataFrame): The DataFrame containing the data.
    value_column (str): The name of the column to be plotted.
    group_column (str): The name of the column to group by.
    title (str, optional): Title for the plot. Defaults to 'Boxplot'.
    xlabel (str, optional): Label for the x-axis. Defaults to 'Groups'.
    ylabel (str, optional): Label for the y-axis. Defaults to 'Values'.
    figsize (tuple, optional): Size of the figure (width, height). Defaults to (10, 6).
    title_fontsize (int, optional): Font size for the title. Defaults to 16.
    label_fontsize (int, optional): Font size for axis labels. Defaults to 14.
    tick_fontsize (int, optional): Font size for tick labels. Defaults to 12.
    dpi (int, optional): Dots per inch for the figure resolution. Defaults to 100.
    outlier_threshold (float, optional): Values greater than this threshold will be excluded from the plot.
    group_values (list, optional): Specific values of the group_column to include in the plot.
    """
    
    # Filter out outliers if an outlier threshold is provided
    if outlier_threshold is not None:
        df = df[df[value_column] <= outlier_threshold]

    # Filter by specific group values if provided
    if group_values is not None:
        df = df[df[group_column].isin(group_values)]

    # Create a figure with specified size and dpi
    plt.figure(figsize=figsize, dpi=dpi)

    # Create the boxplot
    df.boxplot(column=value_column, by=group_column, grid=False, patch_artist=True)

    # Add titles and labels with specified font sizes
    plt.title(title, fontsize=title_fontsize)
    plt.suptitle('')  # Suppress the default title to avoid redundancy
    plt.xlabel(xlabel, fontsize=label_fontsize)
    plt.ylabel(ylabel, fontsize=label_fontsize)

    # Increase font size for tick labels
    plt.xticks(fontsize=tick_fontsize)  # X-axis tick labels
    plt.yticks(fontsize=tick_fontsize)  # Y-axis tick labels

    # Remove spines
    ax = plt.gca()  # Get current axes
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    # Show the plot
    plt.show()
    
##### Using
def boxplot_dataframe_onecategory(df, x, y, title, xlabel, ylabel, figsize=(12, 8), dpi=600, ylim=None):
    """
    Create a box plot of response times split by a specified category with optional y-axis limits.

    Parameters:
    - df: DataFrame containing the data.
    - x: Column name for the x-axis (categorical variable).
    - y: Column name for the y-axis (numerical variable).
    - title: Title of the plot.
    - xlabel: Label for the x-axis.
    - ylabel: Label for the y-axis.
    - figsize: Size of the figure (default is (12, 8)).
    - dpi: Resolution of the figure (default is 600).
    - ylim: Optional tuple specifying the y-axis limits (e.g., (ymin, ymax)). If None, y-axis limits are not set.
    """
    
    # Set the figure size and DPI
    plt.figure(figsize=figsize, dpi=dpi)
    
    # Assign x to hue and use palette for distinct colors
    sns.boxplot(x=x, y=y, data=df, hue=x, palette="pastel", dodge=False, legend=False, width=0.5)
    
    # Customize the plot
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    
    # Set y-axis limits if provided
    if ylim is not None:
        plt.ylim(ylim)
    
    # Remove spines on the right and top
    sns.despine()
    
    # Show the plot
    plt.show()

##### Using
def boxplotDotandDash_dataframe_onecategory(df, x, y, title, xlabel, ylabel, figsize=(12, 8), dpi=600, ylim=None):
    """
    Create a box plot of response times split by a specified category with optional y-axis limits and data points.

    Parameters:
    - df: DataFrame containing the data.
    - x: Column name for the x-axis (categorical variable).
    - y: Column name for the y-axis (numerical variable).
    - title: Title of the plot.
    - xlabel: Label for the x-axis.
    - ylabel: Label for the y-axis.
    - figsize: Size of the figure (default is (12, 8)).
    - dpi: Resolution of the figure (default is 600).
    - ylim: Optional tuple specifying the y-axis limits (e.g., (ymin, ymax)). If None, y-axis limits are not set.
    """
    
    # Set the figure size and DPI
    plt.figure(figsize=figsize, dpi=dpi)
    
    # Create the boxplot
    sns.boxplot(x=x, y=y, data=df, hue=x, palette="pastel", dodge=False, legend=False, width=0.5)
    
    # Overlay data points using stripplot or swarmplot
    sns.stripplot(x=x, y=y, data=df, color='black', alpha=0.5, jitter=True)  # Use jitter=True for random noise
    
    # Alternatively, you can use swarmplot for a different effect
    # sns.swarmplot(x=x, y=y, data=df, color='black', alpha=0.5)

    # Customize the plot
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    
    # Set y-axis limits if provided
    if ylim is not None:
        plt.ylim(ylim)
        
    # Add a dashed line at y=0
    plt.axhline(y=0, color='gray', linestyle='--', linewidth=1)
    
    # Remove spines on the right and top
    sns.despine()
    
    # Show the plot
    plt.show()
    
    


def boxplotDotandDashlinezero_dataframe_onecategory(df, x, y, subject_id, title, xlabel, ylabel, figsize=(12, 8), dpi=600, ylim=None):
    """
    Create a box plot of response times split by a specified category with optional y-axis limits, data points,
    and lines linking data points of the same subject between conditions.

    Parameters:
    - df: DataFrame containing the data.
    - x: Column name for the x-axis (categorical variable).
    - y: Column name for the y-axis (numerical variable).
    - subject_id: Column name for the subject identifier.
    - title: Title of the plot.
    - xlabel: Label for the x-axis.
    - ylabel: Label for the y-axis.
    - figsize: Size of the figure (default is (12, 8)).
    - dpi: Resolution of the figure (default is 600).
    - ylim: Optional tuple specifying the y-axis limits (e.g., (ymin, ymax)). If None, y-axis limits are not set.
    """

    # Set the figure size and DPI
    plt.figure(figsize=figsize, dpi=dpi)

    # Create the boxplot
    sns.boxplot(x=x, y=y, data=df, hue=x, palette="pastel", dodge=False, legend=False, width=0.5)

    # Overlay data points using stripplot or swarmplot
    sns.stripplot(x=x, y=y, data=df, color='black', alpha=0.5, jitter=False)  # Use jitter=True for random noise

    # Alternatively, you can use swarmplot for a different effect
    # sns.swarmplot(x=x, y=y, data=df, color='black', alpha=0.5)

    # Add lines linking data points of the same subject between conditions
    for subject in df[subject_id].unique():
        subject_data = df[df[subject_id] == subject]
        plt.plot(subject_data[x], subject_data[y], color='gray', linestyle='-', linewidth=1, alpha=0.5)

    # Customize the plot
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    # Set y-axis limits if provided
    if ylim is not None:
        plt.ylim(ylim)

    # Add a dashed line at y=0
    plt.axhline(y=0, color='gray', linestyle='--', linewidth=1)

    # Remove spines on the right and top
    sns.despine()

    # Show the plot
    plt.show()    
    

    
##### Using
def boxplotDot_dataframe_onecategory(df, x, y, title, xlabel, ylabel, figsize=(12, 8), dpi=600, ylim=None):
    """
    Create a box plot of response times split by a specified category with optional y-axis limits and data points.

    Parameters:
    - df: DataFrame containing the data.
    - x: Column name for the x-axis (categorical variable).
    - y: Column name for the y-axis (numerical variable).
    - title: Title of the plot.
    - xlabel: Label for the x-axis.
    - ylabel: Label for the y-axis.
    - figsize: Size of the figure (default is (12, 8)).
    - dpi: Resolution of the figure (default is 600).
    - ylim: Optional tuple specifying the y-axis limits (e.g., (ymin, ymax)). If None, y-axis limits are not set.
    """
    
    # Set the figure size and DPI
    plt.figure(figsize=figsize, dpi=dpi)
    
    # Create the boxplot
    sns.boxplot(x=x, y=y, data=df, hue=x, palette="pastel", dodge=False, legend=False, width=0.5)
    
    # Overlay data points using stripplot or swarmplot
    sns.stripplot(x=x, y=y, data=df, color='black', alpha=0.5, jitter=True)  # Use jitter=True for random noise
    
    # Alternatively, you can use swarmplot for a different effect
    # sns.swarmplot(x=x, y=y, data=df, color='black', alpha=0.5)

    # Customize the plot
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    
    # Set y-axis limits if provided
    if ylim is not None:
        plt.ylim(ylim)
        
    # Remove spines on the right and top
    sns.despine()
    
    # Show the plot
    plt.show()
    
    
### Using
import matplotlib.pyplot as plt
import seaborn as sns

def boxplotDotandDashline_dataframe_onecategory(df, x, y, subject_id, title, xlabel, ylabel, figsize=(12, 8), dpi=600, ylim=None):
    """
    Create a box plot of response times split by a specified category with optional y-axis limits, data points,
    and lines linking data points of the same subject between conditions.

    Parameters:
    - df: DataFrame containing the data.
    - x: Column name for the x-axis (categorical variable).
    - y: Column name for the y-axis (numerical variable).
    - subject_id: Column name for the subject identifier.
    - title: Title of the plot.
    - xlabel: Label for the x-axis.
    - ylabel: Label for the y-axis.
    - figsize: Size of the figure (default is (12, 8)).
    - dpi: Resolution of the figure (default is 600).
    - ylim: Optional tuple specifying the y-axis limits (e.g., (ymin, ymax)). If None, y-axis limits are not set.
    """
    
    # Set the figure size and DPI
    plt.figure(figsize=figsize, dpi=dpi)
    
    # Create the boxplot
    sns.boxplot(x=x, y=y, data=df, hue=x, palette="pastel", dodge=False, legend=False, width=0.5)
    
    # Overlay data points using stripplot or swarmplot
    sns.stripplot(x=x, y=y, data=df, color='black', alpha=0.5, jitter=False)  # Use jitter=True for random noise
    
    # Alternatively, you can use swarmplot for a different effect
    # sns.swarmplot(x=x, y=y, data=df, color='black', alpha=0.5)

    # Add lines linking data points of the same subject between conditions
    for subject in df[subject_id].unique():
        subject_data = df[df[subject_id] == subject]
        plt.plot(subject_data[x], subject_data[y], color='gray', linestyle='-', linewidth=1, alpha=0.5)

    # Customize the plot
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    
    # Set y-axis limits if provided
    if ylim is not None:
        plt.ylim(ylim)
        
    # Add a dashed line at y=0
    #plt.axhline(y=0, color='gray', linestyle='--', linewidth=1)
    
    # Remove spines on the right and top
    sns.despine()
    
    # Show the plot
    plt.show()


# def create_boxplot_withLists(list_RTs_ctx, title, xlabel, ylabel, colors=None, 
#                               title_fontsize=16, xlabel_fontsize=14, ylabel_fontsize=14):
#     """
#     Create a boxplot from a list of lists with specified colors.

#     Parameters:
#     list_RTs_ctx (list of lists): A list containing multiple lists of response times.
#     title (str): Title of the boxplot.
#     xlabel (str): Label for the x-axis.
#     ylabel (str): Label for the y-axis.
#     colors (list): A list of colors for each box. If None, default colors will be used.
#     title_fontsize (int): Font size for the title. Defaults to 16.
#     xlabel_fontsize (int): Font size for the x-axis label. Defaults to 14.
#     ylabel_fontsize (int): Font size for the y-axis label. Defaults to 14.
#     """
    
#     # Create the boxplot
#     plt.figure(figsize=(12, 8), dpi=600)
#     bp = plt.boxplot(list_RTs_ctx, patch_artist=True)  # Enable patch_artist to fill colors

#     # Define default colors if none are provided
#     if colors is None:
#         colors = ['lightblue', 'lightgreen', 'rosybrown', 'lightsalmon', 'lightyellow']

#     # Apply colors to each box
#     for patch, color in zip(bp['boxes'], colors):
#         patch.set_facecolor(color)

#     # Add titles and labels with specified font sizes
#     plt.title(title, fontsize=title_fontsize)
#     plt.xlabel(xlabel, fontsize=xlabel_fontsize)
#     plt.ylabel(ylabel, fontsize=ylabel_fontsize)

#     # Set x-axis tick labels
#     plt.xticks([1, 2, 3, 4, 5], ['00', '10', '20', '1', '2'])

#     # Remove spines
#     ax = plt.gca()  # Get current axes
#     ax.spines['right'].set_visible(False)
#     ax.spines['top'].set_visible(False)

#     # Show the plot
#     plt.show()

### Using    
def boxplot_dataframe_twocategories(df, xdata: str, ydata: str, huedata: str, xlabel:str, ylabel: str, title: str, legend_title: str, legend_labels=None):
    """
    Create a boxplot separated by context and follow error.

    Parameters:
    ----------
    df : pandas.DataFrame
        The DataFrame containing the data to be plotted.
        
    xdata : str
        The name of the column in df to be used for the x-axis (context).
        
    ydata : str
        The name of the column in df to be used for the y-axis (response times).
        
    huedata : str
        The name of the column in df to be used for hue (follow error).
        
    ylabel : str
        The label for the y-axis.
        
    title : str
        The title of the plot.
        
    legend_title : str
        Title for the legend.
        
    legend_labels : list of str, optional
        Custom labels for the legend. If None, default labels will be used.

    Returns:
    -------
    None
        Displays the boxplot.
    
    """    
    # Set the figure size and DPI
    plt.figure(figsize=(12, 8), dpi=300)  # Adjust width and height as needed
    
    # Define custom lighter colors for the boxplot
    custom_palette = ['lightgreen', 'lightcoral']  # Specify your desired lighter colors

    # Plotting the boxplot with custom colors
    sns.boxplot(data=df, x=xdata, y=ydata, hue=huedata, palette=custom_palette, dodge=True)
    
    # Overlaying individual data points with stripplot
    sns.stripplot(data=df, x=xdata, y=ydata, hue=huedata, palette=custom_palette,
                  dodge=True, marker='o', alpha=0.9, size=5, edgecolor='black')  # Increased size and added edgecolor

    # Set labels and title
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    # Get current handles and labels from the plot
    handles, _ = plt.gca().get_legend_handles_labels()
    
    # Change legend name and labels if provided
    if legend_labels is not None:
        plt.legend(handles=handles[:len(legend_labels)], title=legend_title, labels=legend_labels)
    else:
        plt.legend(handles=handles[:len(set(df[huedata]))], title=legend_title)

    # Remove right and top spines
    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    # Show the plot
    plt.show()



