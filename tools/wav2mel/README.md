# wav2mel

A neutral, parameterized CLI that converts WAV files to mel-log spectrograms and exports windowed NPY segments.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [CLI Usage](#cli-usage)
- [Outputs](#outputs)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Performance Tips](#performance-tips)

## Overview

`wav2mel` is a command-line tool designed for audio preprocessing in machine learning pipelines. It converts WAV audio files to mel-log spectrograms and segments them into windowed NPY arrays suitable for training datasets.

**When to use:**
- Preparing audio datasets for deep learning models
- Converting raw audio to mel-spectrogram representations
- Creating time-windowed segments for sequence modeling
- Generating standardized audio features across different projects

## Features

- **Flexible Input**: Single WAV file or directory of WAV files
- **Fully Parameterized**: All audio processing parameters configurable via CLI flags
- **Multiple Output Formats**: PNG visualization, NPY arrays (stacked or separate), CSV index
- **Dataset-Ready**: Generates time-aligned segments with precise frame indexing
- **Memory Efficient**: Optional half-precision (float16) output
- **Cross-Platform**: Works on Linux, macOS, and Windows
- **No Dependencies on Project Defaults**: All parameters must be explicitly specified

## Quick Start

```bash
# Basic usage with a single WAV file
wav2mel ./audio.wav --out ./output --sr 44100 --n-mels 64 --win-seconds 1.0 --step-seconds 0.5 --png

# Expected output structure:
output/
├── audio/
│   ├── audio_mel.png          # Full-file mel-spectrogram visualization
│   ├── audio_mel_chunks.npy   # Windowed segments (N, n_mels, frames_per_window)
│   ├── audio_segment_0000.png # Individual segment visualizations (if --save-individual-png)
│   ├── audio_segment_0001.png
│   └── ...
└── index.csv                  # Segment timing and metadata
```

## CLI Usage

### Options Table

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `input` | str | - | Input WAV file or directory containing WAV files |
| `--out` | str | `./out` | Output directory for processed files |
| `--sr` | int | 44100 | Target sample rate (Hz) |
| `--n-fft` | int | 1024 | FFT window size (samples) |
| `--hop` | int | 256 | Hop length between frames (samples) |
| `--n-mels` | int | 64 | Number of mel filter banks |
| `--fmin` | float | 20.0 | Minimum frequency for mel filters (Hz) |
| `--fmax` | float | 16000.0 | Maximum frequency for mel filters (Hz) |
| `--win-seconds` | float | 1.0 | Window duration for segmentation (seconds) |
| `--step-seconds` | float | 0.5 | Step size between windows (seconds) |
| `--pad-last` | flag | False | Pad the last incomplete window |
| `--pad-value` | float | -80.0 | dB value for padding incomplete windows |
| `--save-mode` | choice | `stack` | Output format: `stack` (single NPY) or `separate` (multiple NPY files) |
| `--dtype` | choice | `float32` | NumPy data type: `float32` or `float16` |
| `--save-full-mel` | flag | False | Save complete mel-spectrogram as NPY |
| `--png` | flag | False | Generate PNG visualization of full mel-spectrogram |
| `--save-individual-png` | flag | False | Generate PNG visualization for each NPY segment |
| `--index-csv` | str | `index.csv` | Filename for segment index CSV |
| `--no-center` | flag | False | Disable STFT centering (default: centered) |
| `--mono-strategy` | choice | `mean` | Stereo-to-mono conversion: `mean` or `first` |
| `--top-db` | float | 80.0 | Dynamic range for power-to-dB conversion (dB) |

## Outputs

### PNG Visualization

**Full-file PNG** (`--png`):
- **File**: `{filename}_mel.png`
- **Content**: Full-file mel-log spectrogram
- **Format**: 150 DPI, time (seconds) vs mel bins
- **Units**: Time in seconds, frequency in mel bins, amplitude in dB

**Individual Segment PNGs** (`--save-individual-png`):
- **Files**: `{filename}_segment_{0000}.png`, `{filename}_segment_{0001}.png`, ...
- **Content**: Individual mel-log spectrograms for each NPY segment
- **Format**: 150 DPI, smaller figure size (8x3 inches)
- **Title**: Includes segment index and time range
- **Units**: Time in seconds, frequency in mel bins, amplitude in dB

### NPY Arrays

**Stack Mode** (`--save-mode stack`):
- **File**: `{filename}_mel_chunks.npy`
- **Shape**: `(N_segments, n_mels, frames_per_window)`
- **Data Type**: `float32` or `float16` (per `--dtype`)

**Separate Mode** (`--save-mode separate`):
- **Files**: `{filename}_chunk{0000}.npy`, `{filename}_chunk{0001}.npy`, ...
- **Shape**: `(n_mels, frames_per_window)` per file
- **Data Type**: `float32` or `float16` (per `--dtype`)

**Full Mel-Spectrogram** (`--save-full-mel`):
- **File**: `{filename}_mel_full.npy`
- **Shape**: `(n_mels, total_frames)`
- **Content**: Complete mel-log spectrogram before segmentation

### CSV Index Schema

| Column | Type | Units | Description |
|--------|------|-------|-------------|
| `source_wav` | str | - | Path to source WAV file |
| `npy_path_or_stack` | str | - | Path to NPY file containing segment |
| `segment_idx` | int | - | Segment index within the file |
| `start_frame` | int | frames | Starting frame index in mel-spectrogram |
| `end_frame` | int | frames | Ending frame index in mel-spectrogram |
| `start_time_s` | float | seconds | Starting time in original audio |
| `end_time_s` | float | seconds | Ending time in original audio |
| `sr` | int | Hz | Sample rate used |
| `n_fft` | int | samples | FFT window size |
| `hop` | int | samples | Hop length |
| `n_mels` | int | - | Number of mel filter banks |
| `fmin` | float | Hz | Minimum mel frequency |
| `fmax` | float | Hz | Maximum mel frequency |
| `win_seconds` | float | seconds | Window duration |
| `step_seconds` | float | seconds | Step size between windows |

## Examples

### Directory Input with Stack Mode
```bash
wav2mel ./audio_dataset --out ./processed \
  --sr 22050 --n-fft 2048 --hop 512 \
  --n-mels 128 --fmin 50 --fmax 8000 \
  --win-seconds 2.0 --step-seconds 1.0 \
  --save-mode stack --dtype float32 --png
```

### Separate File Mode with Half Precision
```bash
wav2mel ./long_audio.wav --out ./chunks \
  --sr 44100 --n-fft 1024 --hop 256 \
  --n-mels 64 --fmin 20 --fmax 16000 \
  --win-seconds 0.5 --step-seconds 0.25 \
  --save-mode separate --dtype float16 --save-full-mel
```

### Padding Last Window
```bash
wav2mel ./short_audio.wav --out ./padded \
  --win-seconds 1.0 --step-seconds 0.5 \
  --pad-last --pad-value -100.0
```

### Non-Centered STFT
```bash
wav2mel ./audio.wav --out ./noncentered \
  --no-center --n-fft 1024 --hop 256
```

### Individual Segment Visualizations
```bash
wav2mel ./audio.wav --out ./individual_pngs \
  --win-seconds 0.5 --step-seconds 0.25 \
  --save-individual-png --png
```

## Troubleshooting

### Common Issues

**"No module named 'soundfile'" or libsndfile errors:**
- **macOS**: Install with `brew install libsndfile`
- **Ubuntu/Debian**: Install with `sudo apt-get install libsndfile1`
- **Windows**: Ensure Visual C++ Redistributable is installed

**Memory errors with large files:**
- Use `--dtype float16` to reduce memory usage
- Process files individually instead of entire directories
- Reduce `--n-fft` and increase `--hop` for lower resolution

**Silent or corrupted audio output:**
- Check input WAV file integrity with another audio player
- Verify `--sr` matches your audio's sample rate
- Try different `--mono-strategy` values

**Non-mono WAV files:**
- Use `--mono-strategy mean` for average of channels
- Use `--mono-strategy first` for left channel only

## Performance Tips

### FFT and Hop Length Trade-offs
- **Higher `--n-fft`**: Better frequency resolution, more memory usage
- **Lower `--hop`**: Better time resolution, more frames to process
- **Recommended**: `--n-fft 1024 --hop 256` for speech, `--n-fft 2048 --hop 512` for music

### Data Type Selection
- **`float32`**: Standard precision, larger files, better compatibility
- **`float16`**: Half the storage, faster I/O, potential precision loss
- **Use `float16`** for large datasets where storage is a concern

### Disk I/O Optimization
- **Stack mode**: Faster for sequential access, single file per audio
- **Separate mode**: Better for random access, parallel processing
- **SSD recommended** for large-scale processing
