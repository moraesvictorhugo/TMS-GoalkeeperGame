# The analysis will return:



Blocks were identified using D3 marker

## RMS values trough variables:
### Block variables:
rmsAmplitude_FDI_blockX_V = rms values in a window (time_before_rms = 0.5s) for FDI and block
rmsAmplitude_FDS_blockX_V = rms values in a window (time_before_rms = 0.5s) for FDS and block

### General variables:
rmsAmplitude_FDI_V = concatenation of rmsAmplitude_FDI_blockX_V
rmsAmplitude_FDS_V = concatenation of rmsAmplitude_FDS_blockX_V

## MEP values trough variables:
### Block variables:
MEPpp_FDI_blockX_V = raw FDI MEP amplitudes in Volts considering a window (time_before_stim = 0.01 s and time_after_stim = 0.05 s)
MEPpp_FDS_blockX_V = raw FDS MEP amplitudes in Volts considering a window (time_before_stim = 0.01 s and time_after_stim = 0.05 s)

MEPpp_FDI_withExclusion_blockX_V = raw FDI MEP amplitudes in Volts with outlier exclusions (rms_thresh = 2 sd)
MEPpp_FDS_withExclusion_blockX_V = raw FDS MEP amplitudes in Volts with outlier exclusions (rms_thresh = 2 sd)

relative_MEPpp_FDI_withExclusions_blockX = relative FDI MEP amplitudes with outlier exclusions (normalization = 'normalize_by_mean' or other)
relative_MEPpp_FDS_withExclusions_blockX = relative FDS MEP amplitudes with outlier exclusions (normalization = 'normalize_by_mean' or other)

### General variables:
MEPpp_FDI_V = concatenation of MEPpp_FDI_blockX_V
MEPpp_FDS_V = concatenation of MEPpp_FDS_blockX_V
relative_MEPpp_FDI = relative_MEPpp_FDI_withExclusions_blockX
relative_MEPpp_FDS = relative_MEPpp_FDS_withExclusions_block2

## Behavioral data
### Block variables:
response_times_blockX = time to press the button in trail and block
result_blockX = if sequence and choice match in trial and block
choice_blockX = the choice by volunteer (0,1 or 2) that happened in the trial and block
sequence_blockX = the event (0,1 or 2) that happened in the trial and block

### General variables:
sequence = concatenation of sequence_blockX
choice  = concatenation of choice_blockX
result = concatenation of result_blockX
response_times = concatenation of response_times_blockX
