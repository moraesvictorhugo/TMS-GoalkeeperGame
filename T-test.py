"""
=================================================
Importing modules and data
=================================================
"""
from modules import import_signal
import matplotlib.pyplot as plt
import numpy as np
import pingouin as pg

## Importing processed csv file
file_path = "/home/victormoraes/MEGA/Archive/IBCCF/Projeto Doc/EMT no Jogo do goleiro/Data processing/TMS-GKg_Analysis/"
file_name = "df_gklab_analysis.csv"
df = import_signal.import_csv_data(file_path, file_name)

"""
=================================================
Filtering data
=================================================
"""
# Filter MEPs during pulses and split by context
v01_ctx_2_df = df.loc[(df['tms_pulse'] == 'Pulse') & (df['context'] == 2) & (df['ID_info'] == 1)]
v01_ctx_10_df = df.loc[(df['tms_pulse'] == 'Pulse') & (df['context'] == 10) & (df['ID_info'] == 1)]

# Array for MEPs in ctx 2 and 10
array_v01_ctx_2 = v01_ctx_2_df['relMean_MEPpp_FDI'].to_numpy()
array_v01_ctx_10 = v01_ctx_10_df['relMean_MEPpp_FDI'].to_numpy()

"""
=================================================
T-test
=================================================
"""
# T-test
ttest_results_v01 = pg.ttest(array_v01_ctx_2, array_v01_ctx_10, paired=False, alternative='two-sided', confidence=0.95)

# -----------------------------------------------------------------------------------------------------------------------

"""
=================================================
Filtering data
=================================================
"""
# Filter MEPs during pulses and split by context
v02_ctx_2_df = df.loc[(df['tms_pulse'] == 'Pulse') & (df['context'] == 2) & (df['ID_info'] == 2)]
v02_ctx_10_df = df.loc[(df['tms_pulse'] == 'Pulse') & (df['context'] == 10) & (df['ID_info'] == 2)]

# Array for MEPs in ctx 2 and 10
array_v02_ctx_2 = v02_ctx_2_df['relMean_MEPpp_FDI'].to_numpy()
array_v02_ctx_10 = v02_ctx_10_df['relMean_MEPpp_FDI'].to_numpy()

"""
=================================================
T-test
=================================================
"""
# T-test
ttest_results_v02 = pg.ttest(array_v02_ctx_2, array_v02_ctx_10, paired=False, alternative='two-sided', confidence=0.95)

# -----------------------------------------------------------------------------------------------------------------------

"""
=================================================
Filtering data
=================================================
"""
# Filter MEPs during pulses and split by context
v03_ctx_2_df = df.loc[(df['tms_pulse'] == 'Pulse') & (df['context'] == 2) & (df['ID_info'] == 3)]
v03_ctx_10_df = df.loc[(df['tms_pulse'] == 'Pulse') & (df['context'] == 10) & (df['ID_info'] == 3)]

# Array for MEPs in ctx 2 and 10
array_v03_ctx_2 = v03_ctx_2_df['relMean_MEPpp_FDI'].to_numpy()
array_v03_ctx_10 = v03_ctx_10_df['relMean_MEPpp_FDI'].to_numpy()

"""
=================================================
T-test
=================================================
"""
# T-test
ttest_results_v03 = pg.ttest(array_v03_ctx_2, array_v03_ctx_10, paired=False, alternative='two-sided', confidence=0.95)

# -----------------------------------------------------------------------------------------------------------------------

"""
=================================================
Filtering data
=================================================
"""
# Filter MEPs during pulses and split by context
v04_ctx_2_df = df.loc[(df['tms_pulse'] == 'Pulse') & (df['context'] == 2) & (df['ID_info'] == 4)]
v04_ctx_10_df = df.loc[(df['tms_pulse'] == 'Pulse') & (df['context'] == 10) & (df['ID_info'] == 4)]

# Array for MEPs in ctx 2 and 10
array_v04_ctx_2 = v04_ctx_2_df['relMean_MEPpp_FDI'].to_numpy()
array_v04_ctx_10 = v04_ctx_10_df['relMean_MEPpp_FDI'].to_numpy()

"""
=================================================
T-test
=================================================
"""
# T-test
ttest_results_v04 = pg.ttest(array_v04_ctx_2, array_v04_ctx_10, paired=False, alternative='two-sided', confidence=0.95)

# -----------------------------------------------------------------------------------------------------------------------

"""
=================================================
Filtering data
=================================================
"""
# Filter MEPs during pulses and split by context
v05_ctx_2_df = df.loc[(df['tms_pulse'] == 'Pulse') & (df['context'] == 2) & (df['ID_info'] == 5)]
v05_ctx_10_df = df.loc[(df['tms_pulse'] == 'Pulse') & (df['context'] == 10) & (df['ID_info'] == 5)]

# Array for MEPs in ctx 2 and 10
array_v05_ctx_2 = v05_ctx_2_df['relMean_MEPpp_FDI'].to_numpy()
array_v05_ctx_10 = v05_ctx_10_df['relMean_MEPpp_FDI'].to_numpy()

"""
=================================================
T-test
=================================================
"""
# T-test
ttest_results_v05 = pg.ttest(array_v05_ctx_2, array_v05_ctx_10, paired=False, alternative='two-sided', confidence=0.95)

# -----------------------------------------------------------------------------------------------------------------------

"""
=================================================
Filtering data
=================================================
"""
# Filter MEPs during pulses and split by context
v06_ctx_2_df = df.loc[(df['tms_pulse'] == 'Pulse') & (df['context'] == 2) & (df['ID_info'] == 6)]
v06_ctx_10_df = df.loc[(df['tms_pulse'] == 'Pulse') & (df['context'] == 10) & (df['ID_info'] == 6)]

# Array for MEPs in ctx 2 and 10
array_v06_ctx_2 = v06_ctx_2_df['relMean_MEPpp_FDI'].to_numpy()
array_v06_ctx_10 = v06_ctx_10_df['relMean_MEPpp_FDI'].to_numpy()

"""
=================================================
T-test
=================================================
"""
# T-test
ttest_results_v06 = pg.ttest(array_v06_ctx_2, array_v06_ctx_10, paired=False, alternative='two-sided', confidence=0.95)

# -----------------------------------------------------------------------------------------------------------------------

"""
=================================================
Filtering data
=================================================
"""
# Filter MEPs during pulses and split by context
v07_ctx_2_df = df.loc[(df['tms_pulse'] == 'Pulse') & (df['context'] == 2) & (df['ID_info'] == 7)]
v07_ctx_10_df = df.loc[(df['tms_pulse'] == 'Pulse') & (df['context'] == 10) & (df['ID_info'] == 7)]

# Array for MEPs in ctx 2 and 10
array_v07_ctx_2 = v07_ctx_2_df['relMean_MEPpp_FDI'].to_numpy()
array_v07_ctx_10 = v07_ctx_10_df['relMean_MEPpp_FDI'].to_numpy()

"""
=================================================
T-test
=================================================
"""
# T-test
ttest_results_v07 = pg.ttest(array_v07_ctx_2, array_v07_ctx_10, paired=False, alternative='two-sided', confidence=0.95)

# -----------------------------------------------------------------------------------------------------------------------

"""
=================================================
Filtering data
=================================================
"""
# Filter MEPs during pulses and split by context
v08_ctx_2_df = df.loc[(df['tms_pulse'] == 'Pulse') & (df['context'] == 2) & (df['ID_info'] == 8)]
v08_ctx_10_df = df.loc[(df['tms_pulse'] == 'Pulse') & (df['context'] == 10) & (df['ID_info'] == 8)]

# Array for MEPs in ctx 2 and 10
array_v08_ctx_2 = v08_ctx_2_df['relMean_MEPpp_FDI'].to_numpy()
array_v08_ctx_10 = v08_ctx_10_df['relMean_MEPpp_FDI'].to_numpy()

"""
=================================================
T-test
=================================================
"""
# T-test
ttest_results_v08 = pg.ttest(array_v08_ctx_2, array_v08_ctx_10, paired=False, alternative='two-sided', confidence=0.95)

# -----------------------------------------------------------------------------------------------------------------------

"""
=================================================
Filtering data
=================================================
"""
# Filter MEPs during pulses and split by context
v09_ctx_2_df = df.loc[(df['tms_pulse'] == 'Pulse') & (df['context'] == 2) & (df['ID_info'] == 9)]
v09_ctx_10_df = df.loc[(df['tms_pulse'] == 'Pulse') & (df['context'] == 10) & (df['ID_info'] == 9)]

# Array for MEPs in ctx 2 and 10
array_v09_ctx_2 = v09_ctx_2_df['relMean_MEPpp_FDI'].to_numpy()
array_v09_ctx_10 = v09_ctx_10_df['relMean_MEPpp_FDI'].to_numpy()

"""
=================================================
T-test
=================================================
"""
# T-test
ttest_results_v09 = pg.ttest(array_v09_ctx_2, array_v09_ctx_10, paired=False, alternative='two-sided', confidence=0.95)

# -----------------------------------------------------------------------------------------------------------------------

"""
=================================================
Filtering data
=================================================
"""
# Filter MEPs during pulses and split by context
v10_ctx_2_df = df.loc[(df['tms_pulse'] == 'Pulse') & (df['context'] == 2) & (df['ID_info'] == 10)]
v10_ctx_10_df = df.loc[(df['tms_pulse'] == 'Pulse') & (df['context'] == 10) & (df['ID_info'] == 10)]

# Array for MEPs in ctx 2 and 10
array_v10_ctx_2 = v10_ctx_2_df['relMean_MEPpp_FDI'].to_numpy()
array_v10_ctx_10 = v10_ctx_10_df['relMean_MEPpp_FDI'].to_numpy()

"""
=================================================
T-test
=================================================
"""
# T-test
ttest_results_v10 = pg.ttest(array_v10_ctx_2, array_v10_ctx_10, paired=False, alternative='two-sided', confidence=0.95)

# -----------------------------------------------------------------------------------------------------------------------
