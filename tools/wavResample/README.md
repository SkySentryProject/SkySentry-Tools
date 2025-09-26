# wavResample

A professional WAV resampling tool that intelligently converts audio files to a target sample rate (default: 44.1kHz) with automatic sample rate detection and batch processing capabilities.

## Features

- **Intelligent Sample Rate Handling**: Automatically detects input sample rates and applies appropriate resampling rules
- **Batch Processing**: Process single files or entire directories while preserving folder structure
- **Professional Quality**: Uses `scipy.signal.resample_poly` for high-quality resampling
- **Flexible Options**: Configurable downsampling and overwrite behavior
- **Comprehensive Logging**: Detailed processing information and error reporting

## Quick Start

```bash
# Basic usage - resample a single file
wavResample input.wav --output ./output

# Process entire directory
wavResample ./audio_files --output ./resampled

# Enable downsampling of high sample rate files
wavResample ./audio_files --output ./resampled --downsample

# Overwrite existing files
wavResample ./audio_files --output ./resampled --overwrite
```

## Resampling Rules

The tool applies the following intelligent rules based on input sample rate:

| Input Sample Rate | Action | Output |
|------------------|--------|---------|
| < 16kHz | **Skip** | File rejected (too low quality) |
| 16kHz | **Resample** | Converted to 44.1kHz |
| 44.1kHz | **Copy** | File copied as-is |
| > 44.1kHz | **Skip** (unless `--downsample`) | File skipped or downsampled |

*Note: The minimum sample rate (16kHz) and target sample rate (44.1kHz) can be customized using CLI flags.*

## Command Line Options

### Required Arguments

- `input`: Input WAV file or directory containing WAV files

### Optional Arguments

- `--output DIR`: Output directory (default: `./resampled_output`)
- `--downsample`: Enable downsampling of files with sample rates above target
- `--overwrite`: Overwrite existing output files
- `--verbose`: Enable detailed logging output
- `--min-sample-rate RATE`: Minimum sample rate threshold (default: 16000Hz)
- `--target-sample-rate RATE`: Target sample rate for output (default: 44100Hz)
- `--target-sample-rate-k RATE`: Target sample rate in kHz for filename (default: 44.1k)

## Examples

### Single File Processing

```bash
# Resample a single file
wavResample audio_22k.wav --output ./output
# Output: ./output/audio_22k_44.1k.wav

# With verbose output
wavResample audio_22k.wav --output ./output --verbose

# Custom target sample rate
wavResample audio_22k.wav --output ./output --target-sample-rate 48000 --target-sample-rate-k 48
# Output: ./output/audio_22k_48k.wav
```

### Batch Processing

```bash
# Process all WAV files in a directory
wavResample ./raw_audio --output ./processed_audio

# Process with downsampling enabled
wavResample ./high_quality_audio --output ./standard_audio --downsample

# Process and overwrite existing files
wavResample ./audio_files --output ./resampled --overwrite

# Custom sample rate settings
wavResample ./audio_files --output ./resampled --min-sample-rate 8000 --target-sample-rate 48000 --target-sample-rate-k 48
```

### Advanced Usage

```bash
# Process with all options enabled
wavResample ./mixed_audio --output ./standardized --downsample --overwrite --verbose

# Custom configuration for professional audio
wavResample ./audio_files --output ./professional --min-sample-rate 22050 --target-sample-rate 48000 --target-sample-rate-k 48 --downsample
```

## Output File Naming

Output files are automatically named using the pattern:
```
{original_name}_{target_sample_rate_k}k.wav
```

Examples (with default 44.1kHz target):
- `audio_22k.wav` → `audio_22k_44.1k.wav`
- `recording_96k.wav` → `recording_96k_44.1k.wav`
- `mono_16k.wav` → `mono_16k_44.1k.wav`

Examples (with custom 48kHz target):
- `audio_22k.wav` → `audio_22k_48k.wav`
- `recording_96k.wav` → `recording_96k_48k.wav`

## Folder Structure Preservation

When processing directories, the tool preserves the original folder structure:

```
input/
├── folder1/
│   ├── audio1.wav
│   └── audio2.wav
└── folder2/
    └── audio3.wav

output/
├── folder1/
│   ├── audio1_44.1k.wav
│   └── audio2_44.1k.wav
└── folder2/
    └── audio3_44.1k.wav
```

## Programmatic Usage

The tool can also be used as a Python library:

```python
from tools.wavResample import detect_sr, resample_to_target, process_file
from pathlib import Path

# Detect sample rate
sr = detect_sr(Path("audio.wav"))
print(f"Sample rate: {sr}Hz")

# Resample audio data
import soundfile as sf
audio_data, orig_sr = sf.read("audio.wav")
resampled_data = resample_to_target(audio_data, orig_sr, 44100)  # Target 44.1kHz

# Process a file
result = process_file(
    Path("input.wav"), 
    Path("./output"),
    16000,  # min_sr
    44100,  # target_sr
    44.1,   # target_sr_k
    downsample=True, 
    overwrite=False
)
print(f"Action: {result['action']}, Reason: {result['reason']}")
```

## Technical Details

### Resampling Algorithm

- Uses `scipy.signal.resample_poly` for high-quality polyphase resampling
- Automatically calculates optimal up/down sampling ratios
- Preserves audio quality with minimal artifacts

### Supported Formats

- **Input**: WAV files (mono/stereo, any sample rate)
- **Output**: WAV files at target sample rate (default: 44.1kHz, preserves original bit depth and channels)

### Performance

- Optimized for batch processing of large audio collections
- Progress tracking with `tqdm` for long operations
- Memory-efficient processing of large files

## Error Handling

The tool provides comprehensive error handling:

- **Invalid files**: Skipped with clear error messages
- **Permission errors**: Reported with file paths
- **Corrupted audio**: Detected and skipped
- **Disk space**: Checked before processing

## Logging

The tool provides detailed logging information:

```
INFO: Processing audio_22k.wav: detected 22050Hz
INFO:   → resampled: Resampled from 22050Hz to 48000Hz
INFO: Processing audio_48k.wav: detected 48000Hz
INFO:   → copied: Sample rate already 48000Hz
```

Use `--verbose` for additional debug information.

## Troubleshooting

### Common Issues

**"No WAV files found"**
- Ensure input path contains `.wav` files
- Check file extensions are lowercase

**"Sample rate too low"**
- Files below the minimum sample rate (default: 16kHz) are automatically rejected
- This is intentional to maintain audio quality
- Use `--min-sample-rate` to adjust the threshold

**"Output file exists"**
- Use `--overwrite` to replace existing files
- Or choose a different output directory

**"Permission denied"**
- Check write permissions for output directory
- Ensure input files are not locked by other applications

### Performance Tips

- Use SSD storage for better I/O performance
- Process files in smaller batches for very large collections
- Enable `--verbose` to monitor progress and identify bottlenecks

## Integration

This tool integrates seamlessly with the SkySentry Tools ecosystem:

- Follows the same CLI patterns as other tools
- Compatible with existing audio processing workflows
- Can be chained with other tools in the collection

## License

Part of the SkySentry Tools collection. See the main project LICENSE file for details.
