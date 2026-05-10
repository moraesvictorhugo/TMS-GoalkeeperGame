


df_mean = (
    df.groupby(['volunteer', 'block_info', 'context', 'last_random_was_error'], as_index=False)
      [['MEPpp_FDI_µV', 'MEPpp_FDS_µV']]
      .mean()
)
