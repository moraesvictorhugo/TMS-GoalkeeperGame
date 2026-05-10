import pandas as pd

file_path = '/home/victormoraes/MEGA/Archive/PhD IBCCF-UFRJ/PhD/EMT no Jogo do goleiro/Data processing/data_TMS-GKg/Processed_data/2025-11-18'
file_name = "df_gkg-tms_2.csv"
df = pd.read_csv(file_path + '/' + file_name)

df_mean = (
    df.groupby(['volunteer', 'block_info', 'context', 'last_random_was_error'], as_index=False)
      [['MEPpp_FDI_µV', 'MEPpp_FDS_µV', 'response_time']]
      .mean()
)
