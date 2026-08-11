# TMS-GoalkeeperGame

Research pipeline for processing and analysing transcranial magnetic stimulation (TMS) and electromyography (EMG) data collected during a goalkeeper anticipation game. The project combines a Python pre-processing pipeline (built on MNE) with R statistical analyses to study how predictability and previous outcomes shape motor-evoked potentials (MEPs) in the first dorsal interosseous (FDI) and flexor digitorum superficialis (FDS) muscles, as well as response times (RT).

## Pipeline overview

- **Python signal-processing pipeline** – imports BrainVision recordings, filters the signal, extracts event markers, computes peak-to-peak MEP amplitudes and pre-stimulus RMS, applies outlier exclusion (RMS- or IQR-based), normalizes the MEPs (if needed), and exports the results as CSV format.
- **R statistical analysis** – fits linear mixed-effects models (robust random-slope and simplest random-intercept variants) and aggregated repeated-measures ANOVAs for FDI MEPs, FDS MEPs and RT. Also includes success-rate analysis of the game task.

## Project layout

- `main_processing.py` – main entry point for the Python pre-processing pipeline.
- `modules/` – Python modules used by the pipeline:
  - `import_signal.py` – locate and read BrainVision `.vhdr` recordings.
  - `signal_processing.py` – filtering, event handling, MEP/RMS extraction, normalisation.
  - `plot_data.py` – visualisation helpers for EMG, RMS and MEP amplitudes and success rates.
  - `export_data.py` – CSV export helpers (including GKlAB format).
  - `analysis.py` – success-rate and context/error computations.
  - `utils.py` – marker handling and miscellaneous helpers.
- `main_stats_fdi_meps.R`, `main_stats_fds_meps.R`, `main_stats_rt_.R` – LME models and RM-ANOVAs for FDI MEPs, FDS MEPs and response time.
- `successRate_analisys.R` – success-rate analysis of the game task (Kruskal–Wallis + Dunn post-hoc).
- `geometric means_plots.R` – geometric-mean figure generation for per-participant and group curves.
- `analysis_outputs/` – generated figures (PDF and PNG).
- `pyproject.toml`, `renv.lock` – Python and R dependency management.

## Dependencies

- **Python** (>= 3.11): MNE, NumPy, SciPy, pandas, matplotlib, seaborn, scikit-learn, statsmodels. Install with `uv sync` or `pip install -e .` using `pyproject.toml`.
- **R**: tidyverse, lme4, lmerTest, performance, see, emmeans, effectsize, rstatix, ggplot2, ggpubr. An `renv` lockfile is provided.

## Scripts overview

| Script | Purpose |
| ------ | ------- |
| `main_processing.py` | Pre-process a single participant's TMS/EMG recording and export trial data. |
| `main_stats_fdi_meps.R` | Statistical analysis of FDI MEP amplitudes. |
| `main_stats_fds_meps.R` | Statistical analysis of FDS MEP amplitudes. |
| `main_stats_rt_.R` | Statistical analysis of response times. |
| `successRate_analisys.R` | Success-rate analysis across game blocks. |
| `geometric means_plots.R` | Build geometric-mean figures for FDI MEPs, FDS MEPs and RT. |

## Disclaimer

Research code. Data file paths (Python and R scripts) point to machine-specific locations and should be adjusted before running on another system.