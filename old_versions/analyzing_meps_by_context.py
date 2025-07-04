import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file
df_meps_ctx = pd.read_csv('/home/victormoraes/MEGA/Resources/Working/Matlab analysis/MEPs_CTX/df_meps_ctx.csv')
# df_meps_ctx = pd.read_csv('/home/victormoraes/MEGA/Archive/IBCCF/Projeto Doc/EMT no Jogo do goleiro/Data processing/Scripts_bkp/MATLAB Analysis/v01_meps_by_ctx.csv')

# Set figure size
plt.figure(figsize=(14, 8))  # Adjust width and height as needed

# Delete outliers
df_meps_ctx = df_meps_ctx[df_meps_ctx["rel_meps"] <= 1000]

# Plot the violin plot
sns.violinplot(x=df_meps_ctx["ctx"], y=df_meps_ctx["rel_meps"], palette='Set2')

# ---------------------------------------------------------------------------------------------------------------------------

import seaborn as sns
import pandas as pd

# # Read the CSV file
# df_meps_ctx = pd.read_csv('/home/victormoraes/MEGA/Resources/Working/Matlab analysis/MEPs_CTX/df_meps_ctx.csv')

# Delete outliers
df_meps_ctx = df_meps_ctx[df_meps_ctx["rel_meps"] <= 1000]

# Filter to include only the desired categories
selected_ctx = ["w2", "w10"]  # Replace with your desired categories
filtered_df = df_meps_ctx[df_meps_ctx["ctx"].isin(selected_ctx)]

# Plot the violin plot
sns.violinplot(x='ctx', y='rel_meps', data=filtered_df, palette='Set2')

# ---------------------------------------------------------------------------------------------------------------------------

import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file
df_meps_ctx = pd.read_csv('/home/victormoraes/MEGA/Resources/Working/Matlab analysis/MEPs_CTX/df_meps_ctx.csv')

# Delete outliers
df_meps_ctx = df_meps_ctx[df_meps_ctx["rel_meps"] <= 1000]

# Filter to include only the desired categories
selected_categories = ["w1", "w10"]  # Replace with your desired categories
filtered_df = df_meps_ctx[df_meps_ctx["ctx"].isin(selected_categories)]

# Set up the plot
plt.figure(figsize=(10, 6))

# Plot normalized histograms for each category
for category in selected_categories:
    data = filtered_df[filtered_df["ctx"] == category]["rel_meps"]
    plt.hist(data, bins=30, density=True, alpha=0.5, label=category)

# Add labels and title
plt.xlabel('Relative MEPs')
plt.ylabel('Density')
plt.title('Normalized Histogram of Relative MEPs for Selected Categories')
plt.legend(title='Context')

# Show the plot
plt.show()

# ---------------------------------------------------------------------------------------------------------------------------
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file
df_meps_ctx = pd.read_csv('/home/victormoraes/MEGA/Resources/Working/Matlab analysis/MEPs_CTX/df_meps_ctx.csv')

# Delete outliers
df_meps_ctx = df_meps_ctx[df_meps_ctx["rel_meps"] <= 1000]

# Filter to include only the desired categories
selected_categories = ["w00", "w10"]  # Replace with your desired categories
filtered_df = df_meps_ctx[df_meps_ctx["ctx"].isin(selected_categories)]

# Set up the plot
plt.figure(figsize=(10, 6))

# Set a color palette
colors = sns.color_palette("Set2", len(selected_categories))

# Plot normalized histogram and KDE for each category
for category, color in zip(selected_categories, colors):
    data = filtered_df[filtered_df["ctx"] == category]["rel_meps"]
    
    # Plot histogram with KDE
    sns.histplot(data, bins=30, kde=True, stat="density", alpha=0.5, label=f' {category}', color=color)
    
# Add labels and title
plt.xlabel('Relative MEPs')
plt.ylabel('Density')
plt.title('Normalized Histogram and KDE of Relative MEPs')
plt.legend(title='Context')

# Show the plot
plt.show()

# ---------------------------------------------------------------------------------------------------------------------------
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file
df_meps_ctx = pd.read_csv('/home/victormoraes/MEGA/Resources/Working/Matlab analysis/MEPs_CTX/df_meps_ctx.csv')

# Delete outliers
df_meps_ctx = df_meps_ctx[df_meps_ctx["rel_meps"] <= 1000]

# Filter to include only the desired categories
selected_categories = ["w2", "w10"]  # Replace with your actual categories
filtered_df = df_meps_ctx[df_meps_ctx["ctx"].isin(selected_categories)]

# Calculate means and standard deviations
summary_stats = filtered_df.groupby("ctx")["rel_meps"].agg(["mean", "std"]).reset_index()

# Set up the plot
plt.figure(figsize=(10, 6))

# Create a bar plot with mean and standard deviation
sns.barplot(x='ctx', y='mean', data=summary_stats, palette='Set2', ci=None)

# Add error bars for standard deviation
for index, row in summary_stats.iterrows():
    plt.errorbar(row['ctx'], row['mean'], yerr=row['std'], fmt='none', c='black', capsize=5)

# Add labels and title
plt.xlabel('Context')
plt.ylabel('Mean Relative MEPs')
plt.title('Mean Relative MEPs with Standard Deviation by Context')

# Show the plot
plt.show()

# ---------------------------------------------------------------------------------------------------------------------------

import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file
df_meps_ctx = pd.read_csv('/home/victormoraes/MEGA/Resources/Working/Matlab analysis/MEPs_CTX/df_meps_ctx.csv')

# Delete outliers
df_meps_ctx = df_meps_ctx[df_meps_ctx["rel_meps"] <= 1000]

# Calculate means and standard deviations for all categories
summary_stats = df_meps_ctx.groupby("ctx")["rel_meps"].agg(["mean", "std"]).reset_index()

# Set up the plot
plt.figure(figsize=(10, 6))

# Create a bar plot with mean and standard deviation for all categories
sns.barplot(x='ctx', y='mean', data=summary_stats, palette='Set2', ci=None)

# Add error bars for standard deviation
for index, row in summary_stats.iterrows():
    plt.errorbar(row['ctx'], row['mean'], yerr=row['std'], fmt='none', c='black', capsize=5)

# Add labels and title
plt.xlabel('Context')
plt.ylabel('Mean Relative MEPs')
plt.title('Mean Relative MEPs with Standard Deviation by Context')

# Show the plot
plt.xticks(rotation=45)  # Rotate x labels for better readability
plt.tight_layout()  # Adjust layout to fit everything
plt.show()

# -------------------------------------------------------------------------------------
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Read the CSV file and split the single column into multiple columns
df_meps_ctx = pd.read_csv('/home/victormoraes/MEGA/Resources/Working/Matlab analysis/MEPs_CTX/meps_by_cts_all_volunteers.csv', sep=';')

# Delete outliers
df_meps_ctx = df_meps_ctx[df_meps_ctx["mep"] <= 1000]

# Create the boxplot (without palette)
plt.figure(figsize=(14, 8))  # Adjust the figure size as needed
sns.boxplot(x='ctx', y='mep', data=df_meps_ctx)  # Boxplot with 'ctx' on X and 'mep' on Y

# Add the dots colored by 'vol'
sns.stripplot(x='ctx', y='mep', data=df_meps_ctx, hue='vol', palette='coolwarm', dodge=True, jitter=True, size=5)

# Add title and labels
plt.title('Boxplot with Individual MEPs', fontsize=14)
plt.xlabel('Context (ctx)', fontsize=12)
plt.ylabel('MEP', fontsize=12)

# Adjust the legend (this should fix the issue)
handles, labels = plt.gca().get_legend_handles_labels()
plt.legend(handles=handles[:len(df_meps_ctx['vol'].unique())], title='Volunteers', bbox_to_anchor=(1.05, 1), loc='upper left')

# Save the figure before showing it (optional)
# plt.tight_layout()
# plt.savefig('boxplot_mep_vol_ctx.png', dpi=300, bbox_inches='tight')  # Save the figure as a PNG file with high resolution

# Display the plot
plt.tight_layout()
plt.show()

# -----------------------------------------------------------------------------

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Read the CSV file and split the single column into multiple columns
df_meps_ctx = pd.read_csv('/home/victormoraes/MEGA/Resources/Working/Matlab analysis/MEPs_CTX/meps_by_cts_all_volunteers.csv', sep=';')

# Delete outliers
df_meps_ctx = df_meps_ctx[df_meps_ctx["mep"] <= 1000]

# Ensure the 'vol' column is treated as categorical (if it isn't already)
df_meps_ctx['vol'] = df_meps_ctx['vol'].astype('category')

# Create the boxplot (without palette)
plt.figure(figsize=(14, 8))  # Adjust the figure size as needed
sns.boxplot(x='ctx', y='mep', data=df_meps_ctx)  # Boxplot with 'ctx' on X and 'mep' on Y

# Add the dots colored by 'vol', using explicit hue order to ensure all volunteers are shown
unique_volunteers = df_meps_ctx['vol'].unique()
sns.stripplot(x='ctx', y='mep', data=df_meps_ctx, hue='vol', palette='coolwarm', dodge=True, jitter=True, size=5, hue_order=unique_volunteers)

# Add title and labels
plt.title('Boxplot with Individual MEPs', fontsize=14)
plt.xlabel('Context (ctx)', fontsize=12)
plt.ylabel('Relative MEP amplitudes', fontsize=12)

# Adjust the legend to show all volunteers
plt.legend(title='Volunteers', bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0., ncol=1)

# Save the figure before showing it (optional)
plt.tight_layout()
plt.savefig('boxplot_mep_vol_ctx.png', dpi=300, bbox_inches='tight')  # Save the figure as a PNG file with high resolution

# Display the plot
plt.tight_layout()
plt.show()
