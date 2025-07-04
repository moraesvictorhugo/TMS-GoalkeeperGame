"""
=================================================
Importing data
=================================================
"""
import mne
import pathlib
import pandas as pd

def find_vhdr_file(folder_name):
    root_folder = pathlib.Path('data_TMS-GKg')
    folder_path = root_folder / folder_name
    for file in folder_path.iterdir():
        if file.suffix == '.vhdr':
            return file.resolve()
    return None

def import_brainvision_data(fname):
    """Imports EEG/EMG data from a BrainVision file."""
    return mne.io.read_raw_brainvision(fname, preload=True)

def import_csv_data(file_path, file_name):
    """
    Import a CSV file from a specified path.    
    Returns:
        pd.DataFrame: The imported DataFrame.
    """
    return pd.read_csv(file_path + '/' + file_name, encoding='utf-7')
   
