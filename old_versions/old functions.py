
#################### To make plots

# def plot_success_rates_by_blocks_group(df):
#     """
#     Create boxplots showing success rates for each block, with data grouped by volunteers (ID_info).

#     Parameters:
#     df (pd.DataFrame): A DataFrame containing 'ID_info', 'block_info', 'response_info', and 'stochastic_chain_info'.
#     """
#     # Calculate success rates by ID and block
#     results = {}

#     # Group by 'ID_info'
#     for id_value, group in df.groupby('ID_info'):
#         # For each ID, calculate success rates for each block
#         success_rates = group.groupby('block_info').apply(
#             lambda block: (block['response_info'] == block['stochastic_chain_info']).mean()
#         ).to_dict()
        
#         # Store the results in the dictionary
#         results[id_value] = success_rates

#     # Prepare data for plotting
#     plot_data = []
    
#     for id_value, blocks in results.items():
#         for block, rate in blocks.items():
#             plot_data.append({'ID_info': id_value, 'block_info': block, 'success_rate': rate})

#     # Create a DataFrame from the prepared data
#     plot_df = pd.DataFrame(plot_data)

#     # Define colors for volunteers (dots)
#     unique_volunteer_colors = sns.color_palette("husl", len(plot_df['ID_info'].unique()))
#     volunteer_color_map = {id_value: unique_volunteer_colors[i] for i, id_value in enumerate(plot_df['ID_info'].unique())}

#     # Create boxplots with hue assignment
#     plt.figure(figsize=(10, 6), dpi=900)
#     ax = sns.boxplot(x='block_info', y='success_rate', data=plot_df, hue='block_info', palette='pastel', showmeans=True, dodge=False)

#     # Set transparency for the boxplot faces
#     for patch in ax.patches:
#         r, g, b, _ = patch.get_facecolor()  # Get current face color (RGBA)
#         patch.set_facecolor((r, g, b, 0.3))  # Set new face color with transparency

#     # Overlay the volunteer dots with corresponding colors
#     handles = []  # List to store legend handles
#     added_volunteers = set()  # To avoid duplicate legend entries
    
#     # Get x-axis positions of each boxplot category
#     x_positions = {category: i for i, category in enumerate(sorted(plot_df['block_info'].unique()))}

#     for _, row in plot_df.iterrows():
#         dot_color = volunteer_color_map[row['ID_info']]  # Assign a unique color to each volunteer
#         plt.scatter(x=x_positions[row['block_info']], y=row['success_rate'], 
#                     color=dot_color, alpha=0.7, edgecolor='black', s=50)

#         # Add to legend if not already added
#         if row['ID_info'] not in added_volunteers:
#             handles.append(plt.Line2D([0], [0], marker='o', color='w', label=f'V{int(row["ID_info"])}', 
#                                        markerfacecolor=dot_color))
#             added_volunteers.add(row['ID_info'])

#     # Add titles and labels
#     plt.title('Success Rates by Block for Each Volunteer', fontsize=16)
#     plt.xlabel('Block Info', fontsize=14)
#     plt.ylabel('Success Rate', fontsize=14)
    
#     # Set y-axis limits from 0 to 1 for better visualization
#     plt.ylim(0.3, 1)

#     # Increase font size for tick labels
#     plt.xticks(fontsize=12)  # X-axis tick labels
#     plt.yticks(fontsize=12)  # Y-axis tick labels

#     # Create a legend with unique entries for volunteers
#     plt.legend(handles=handles, title="Volunteers", bbox_to_anchor=(1.05, 1), loc='upper left')

#     # Remove right and upper spines
#     ax.spines['right'].set_visible(False)  # Remove right spine
#     ax.spines['top'].set_visible(False)   # Remove top spine

#     # Show the plot
#     plt.tight_layout()
#     plt.show()

# def plot_success_rates_by_blocks_stripplot(df):
#     """
#     Visualize success rates using stripplot with volunteer-specific coloring
    
#     Parameters:
#     df (pd.DataFrame): Contains 'ID_info', 'block_info', 'response_info', 'stochastic_chain_info'
#     """
#     # Calculate success rates
#     plot_df = df.groupby(['ID_info', 'block_info']).apply(
#         lambda x: (x['response_info'] == x['stochastic_chain_info']).mean()
#     ).reset_index(name='success_rate')

#     plt.figure(figsize=(10, 6), dpi=900)
#     ax = sns.stripplot(
#         x='block_info', 
#         y='success_rate', 
#         hue='ID_info',
#         data=plot_df,
#         palette='husl',
#         jitter=0.2,
#         dodge=False,
#         edgecolor='face',  # Match edge color to face color
#         size=8,
#         alpha=0.7
#     )

#     # Add mean indicators
#     sns.pointplot(
#         x='block_info', 
#         y='success_rate', 
#         data=plot_df,
#         estimator=np.mean,
#         color='black',
#         markers='D',
#         errorbar=None  # Remove scale parameter
#     )

#     # Styling
#     plt.title('Success Rates by Block (Strip Plot)', fontsize=16)
#     plt.xlabel('Block', fontsize=14)
#     plt.ylabel('Success Rate', fontsize=14)
#     plt.ylim(0.3, 1)
    
#     # Legend handling - use ax.legend() directly
#     ax.legend(title='Volunteers', bbox_to_anchor=(1.05, 1), loc='upper left')

#     sns.despine()
#     plt.tight_layout()
#     plt.show()

# def plot_boxplot(df, value_column, group_column, title='Boxplot', xlabel='Groups', ylabel='Values',
#                  figsize=(14, 10), title_fontsize=16, label_fontsize=14, tick_fontsize=12, dpi=100,
#                  outlier_threshold=None):
#     """
#     Create a boxplot for a specified value column, grouped by another column.

#     Parameters:
#     df (DataFrame): The DataFrame containing the data.
#     value_column (str): The name of the column to be plotted.
#     group_column (str): The name of the column to group by.
#     title (str, optional): Title for the plot. Defaults to 'Boxplot'.
#     xlabel (str, optional): Label for the x-axis. Defaults to 'Groups'.
#     ylabel (str, optional): Label for the y-axis. Defaults to 'Values'.
#     figsize (tuple, optional): Size of the figure (width, height). Defaults to (10, 6).
#     title_fontsize (int, optional): Font size for the title. Defaults to 16.
#     label_fontsize (int, optional): Font size for axis labels. Defaults to 14.
#     tick_fontsize (int, optional): Font size for tick labels. Defaults to 12.
#     dpi (int, optional): Dots per inch for the figure resolution. Defaults to 100.
#     outlier_threshold (float, optional): Values greater than this threshold will be excluded from the plot.
#     """
    
#     # Filter out outliers if an outlier threshold is provided
#     if outlier_threshold is not None:
#         df = df[df[value_column] <= outlier_threshold]

#     # Create a figure with specified size and dpi
#     plt.figure(figsize=figsize, dpi=dpi)

#     # Create the boxplot
#     df.boxplot(column=value_column, by=group_column, grid=False, patch_artist=True)

#     # Add titles and labels with specified font sizes
#     plt.title(title, fontsize=title_fontsize)
#     plt.suptitle('')  # Suppress the default title to avoid redundancy
#     plt.xlabel(xlabel, fontsize=label_fontsize)
#     plt.ylabel(ylabel, fontsize=label_fontsize)

#     # Increase font size for tick labels
#     plt.xticks(fontsize=tick_fontsize)  # X-axis tick labels
#     plt.yticks(fontsize=tick_fontsize)  # Y-axis tick labels

#     # Remove spines
#     ax = plt.gca()  # Get current axes
#     ax.spines['right'].set_visible(False)
#     ax.spines['top'].set_visible(False)

#     # Show the plot
#     plt.show()

# def boxplot_separated_by_ctx_and_fer(df, xdata: str, ydata: str, huedata: str, ylabel: str, title: str, legend_labels=None):
#     """
#     Create a boxplot separated by context and follow error.

#     This function generates a boxplot using the specified columns from the provided DataFrame.
#     It visualizes the distribution of response times (or any other metric) by context,
#     with optional separation by a follow error category.

#     Parameters:
#     ----------
#     df : pandas.DataFrame
#         The DataFrame containing the data to be plotted.
        
#     xdata : str
#         The name of the column in df to be used for the x-axis (context).
        
#     ydata : str
#         The name of the column in df to be used for the y-axis (response times).
        
#     huedata : str
#         The name of the column in df to be used for hue (follow error).
        
#     ylabel : str
#         The label for the y-axis.
        
#     title : str
#         The title of the plot.
        
#     legend_labels : list of str, optional
#         Custom labels for the legend. If None, default labels will be used.

#     Returns:
#     -------
#     None
#         Displays the boxplot.
    
#     """    
#     # Set the figure size and DPI
#     plt.figure(figsize=(12, 8), dpi=300)  # Adjust width and height as needed
    
#     # Define custom lighter colors for the boxplot
#     custom_palette = ['lightgreen', 'lightcoral']  # Specify your desired lighter colors

#     # Plotting the boxplot with custom colors
#     sns.boxplot(data=df, x=xdata, y=ydata, hue=huedata, palette=custom_palette, dodge=True)
    
#     # Overlaying individual data points with stripplot
#     sns.stripplot(data=df, x=xdata, y=ydata, hue=huedata, palette=custom_palette,
#                   dodge=True, marker='o', alpha=0.9, size=5, edgecolor='black')  # Increased size and added edgecolor

#     # Set labels and title
#     plt.xlabel('Context')
#     plt.ylabel(ylabel)
#     plt.title(title)

#     # Get current handles and labels from the plot
#     handles, _ = plt.gca().get_legend_handles_labels()
    
#     # Change legend name and labels if provided
#     if legend_labels is not None:
#         plt.legend(handles=handles[:len(legend_labels)], title='Previous Result', labels=legend_labels)

#     # Remove right and top spines
#     ax = plt.gca()
#     ax.spines['right'].set_visible(False)
#     ax.spines['top'].set_visible(False)

#     # Show the plot
#     plt.show()

# def plot_mep_amplitudes(rms_time_points, p2p_1, p2p_2, rms_1, rms_2, 
#                         rms_threshold_ch1, rms_threshold_ch2, 
#                         exclusion_threshold_ch1, exclusion_threshold_ch2, 
#                         data_filtered):
#     f, (ax1, ax2) = plt.subplots(1, 2)
#     f.canvas.manager.set_window_title("Figure 8")

#     # Determine excluded MEPs for channel 1
#     excluded_mep_1 = np.where((rms_1 > rms_threshold_ch1) | (p2p_1 * 1e6 < exclusion_threshold_ch1), 
#                                p2p_1 * 1e6, np.nan)
#     ax1.plot(rms_time_points, p2p_1 * 1e6, marker='o', linestyle='None', label='Included MEP')
#     ax1.plot(rms_time_points, excluded_mep_1, 'ro', label='Excluded MEP', alpha=0.5)

#     # Determine excluded MEPs for channel 2
#     excluded_mep_2 = np.where((rms_2 > rms_threshold_ch2) | (p2p_2 * 1e6 < exclusion_threshold_ch2), 
#                                p2p_2 * 1e6, np.nan)
#     ax2.plot(rms_time_points, p2p_2 * 1e6, marker='o', linestyle='None', label='Included MEP')
#     ax2.plot(rms_time_points, excluded_mep_2, 'ro', label='Excluded MEP', alpha=0.5)

#     # Configure the first subplot
#     ax1.set_title(f"MEP Amplitude {data_filtered.ch_names[0]}")
#     ax1.set_xlabel('Time [s]')
#     ax1.set_ylabel('Voltage [µV]')
#     ax1.legend()

#     # Configure the second subplot
#     ax2.set_title(f"MEP Amplitude {data_filtered.ch_names[1]}")
#     ax2.set_xlabel('Time [s]')
#     ax2.set_ylabel('Voltage [µV]')
#     ax2.legend()

#     plt.show()


# def plot_mep_vs_rms(rms_1, rms_2, p2p_1, p2p_2):
#     fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
#     fig.canvas.manager.set_window_title("Figure 9")

#     ax1.scatter(rms_1, p2p_1 * 1e6, color='blue', label='FDI')
#     coeffs_ch1 = np.polyfit(rms_1, p2p_1 * 1e6, 1)
#     trendline_ch1 = np.polyval(coeffs_ch1, rms_1)
#     ax1.plot(rms_1, trendline_ch1, color='red', linestyle='--', label='Trendline')
#     ax1.set_xlabel('RMS Amplitude [µV]')
#     ax1.set_ylabel('MEP Amplitude [µV]')
#     ax1.set_title('FDI')
#     ax1.grid(True)
#     ax1.legend()

#     ax2.scatter(rms_2, p2p_2 * 1e6, color='green', label='FDS')
#     coeffs_ch2 = np.polyfit(rms_2, p2p_2 * 1e6, 1)
#     trendline_ch2 = np.polyval(coeffs_ch2, rms_2)
#     ax2.plot(rms_2, trendline_ch2, color='orange', linestyle='--', label='Trendline')
#     ax2.set_xlabel('RMS Amplitude [µV]')
#     ax2.set_ylabel('MEP Amplitude [µV]')
#     ax2.set_title('FDS')
#     ax2.grid(True)
#     ax2.legend()

#     plt.tight_layout()
#     plt.show()

# def plot_excluded_mep_vs_rms(rms_1, rms_2, p2p_1, p2p_2, excluded_indices_ch1, excluded_indices_ch2):
#     fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
#     fig.canvas.manager.set_window_title("Figure 11")

#     ax1.scatter(rms_1[excluded_indices_ch1], p2p_1[excluded_indices_ch1] * 1e6, color='blue', label='FDI (Excluded)')
#     slope_ch1, intercept_ch1, _, _, _ = linregress(rms_1[excluded_indices_ch1], p2p_1[excluded_indices_ch1] * 1e6)
#     trendline_ch1 = slope_ch1 * rms_1[excluded_indices_ch1] + intercept_ch1
#     ax1.plot(rms_1[excluded_indices_ch1], trendline_ch1, color='red', linestyle='--', label='Trendline')
#     ax1.set_xlabel('RMS Amplitude [µV]')
#     ax1.set_ylabel('MEP Amplitude [µV]')
#     ax1.set_title('FDI - Excluded MEPs')
#     ax1.grid(True)
#     ax1.legend()

#     ax2.scatter(rms_2[excluded_indices_ch2], p2p_2[excluded_indices_ch2] * 1e6, color='green', label='FDS (Excluded)')
#     slope_ch2, intercept_ch2, _, _, _ = linregress(rms_2[excluded_indices_ch2], p2p_2[excluded_indices_ch2] * 1e6)
#     trendline_ch2 = slope_ch2 * rms_2[excluded_indices_ch2] + intercept_ch2
#     ax2.plot(rms_2[excluded_indices_ch2], trendline_ch2, color='orange', linestyle='--', label='Trendline')
#     ax2.set_xlabel('RMS Amplitude [µV]')
#     ax2.set_ylabel('MEP Amplitude [µV]')
#     ax2.set_title('FDS - Excluded MEPs')
#     ax2.grid(True)
#     ax2.legend()

#     plt.tight_layout()
#     plt.show()

# def plot_bar_with_sd(data1, data2, data3, labels=None, title=None):
#     """
#     Plots a bar chart with 3 variables and standard deviation error bars.

#     Parameters:
#     - data1, data2, data3: 1D arrays or lists of data points to calculate mean and standard deviation.
#     - labels: Optional list of labels for each bar group (default is None).
#     """
#     # Remove NaN values and calculate mean and standard deviation for each data set
#     means = [np.nanmean(data1), np.nanmean(data2), np.nanmean(data3)]
#     std_devs = [np.nanstd(data1, ddof=1), np.nanstd(data2, ddof=1), np.nanstd(data3, ddof=1)]
    
#     # Define the position of each bar on the x-axis
#     x_labels = labels if labels else ['Variable 1', 'Variable 2', 'Variable 3']
#     x_pos = np.arange(len(means))

#     # Plot bars with standard deviation error bars
#     plt.bar(x_pos, means, yerr=std_devs, capsize=5, color=['blue', 'orange', 'green'])
    
#     # Add labels and title
#     plt.xticks(x_pos, x_labels)
#     plt.ylabel('Mean and Standard Deviation')
#     plt.title(title)
    
#     # Display the plot
#     plt.show()

# def plot_histogram(data, name, figure_num):
#     """Plot histogram for the given data."""
#     plt.figure(num=figure_num, figsize=(10, 6))  # Set the figure number and window size
#     plt.hist(data, bins=50)
#     plt.title(f'Histogram of {name}')
#     plt.xlabel('Amplitude')
#     plt.ylabel('Frequency')
#     plt.show()

# def plot_multiple_histograms(variable_names, main_variables):
#     """Plot multiple histograms for the given variables."""
#     for index, (name, data) in enumerate(zip(variable_names, main_variables), start=3):
#         plot_histogram(data, name, index)