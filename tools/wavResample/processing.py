"""
Core processing functions for WAV resampling.

This module provides the core functionality for detecting sample rates,
resampling audio to 48kHz, and processing files with proper error handling.
"""

from pathlib import Path
import logging
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Default constants (can be overridden by CLI parameters)
DEFAULT_MIN_SAMPLE_RATE = 16000  # Default minimum sample rate for processing
DEFAULT_TARGET_SAMPLE_RATE = 44100  # Default target sample rate for output
DEFAULT_TARGET_SAMPLE_RATE_K = 44.1  # Default target sample rate in kHz for naming


def detect_sr(filepath: Path) -> int:
    """
    Detect the sample rate of a WAV file.
    
    Args:
        filepath: Path to the WAV file
        
    Returns:
        Sample rate in Hz
        
    Raises:
        RuntimeError: If file cannot be read or is not a valid audio file
    """
    try:
        info = sf.info(str(filepath))
        return info.samplerate
    except Exception as e:
        raise RuntimeError(f"Failed to read audio file {filepath}: {e}")


def resample_to_target(waveform: np.ndarray, sr: int, target_sr: int) -> np.ndarray:
    """
    Resample audio waveform to target sample rate using scipy.signal.resample_poly.
    
    Args:
        waveform: Input audio data (1D for mono, 2D for stereo)
        sr: Original sample rate
        target_sr: Target sample rate
        
    Returns:
        Resampled audio data at target sample rate
        
    Raises:
        ValueError: If sample rate is invalid
    """
    if sr <= 0:
        raise ValueError(f"Invalid sample rate: {sr}")
    
    if sr == target_sr:
        return waveform
    
    # Calculate resampling ratio
    # resample_poly uses up/down factors: target_sr = (up/down) * orig_sr
    # We need: up/down = target_sr / sr
    # Find the simplest integer ratio
    from math import gcd
    
    up = target_sr
    down = sr
    
    # Simplify the ratio
    common_divisor = gcd(up, down)
    up //= common_divisor
    down //= common_divisor
    
    logger.debug(f"Resampling from {sr}Hz to {target_sr}Hz using ratio {up}:{down}")
    
    # Handle both mono and stereo
    if waveform.ndim == 1:
        # Mono
        resampled = resample_poly(waveform, up, down)
    else:
        # Stereo or multi-channel
        expected_length = int(waveform.shape[1] * up / down)
        resampled = np.zeros((waveform.shape[0], expected_length), dtype=waveform.dtype)
        for ch in range(waveform.shape[0]):
            resampled[ch] = resample_poly(waveform[ch], up, down)
    
    return resampled


def process_file(filepath: Path, outdir: Path, min_sr: int, target_sr: int, target_sr_k: float, downsample: bool = False, overwrite: bool = False) -> dict:
    """
    Process a single WAV file according to resampling rules.
    
    Args:
        filepath: Input WAV file path
        outdir: Output directory
        min_sr: Minimum sample rate threshold
        target_sr: Target sample rate for output
        target_sr_k: Target sample rate in kHz for naming
        downsample: Whether to downsample files with higher sample rates
        overwrite: Whether to overwrite existing output files
        
    Returns:
        Dictionary with processing results: {'action': str, 'reason': str, 'output_path': Path}
    """
    try:
        # Detect sample rate
        sr = detect_sr(filepath)
        logger.info(f"Processing {filepath.name}: detected {sr}Hz")
        
        # Apply resampling rules
        if sr < min_sr:
            return {
                'action': 'skipped',
                'reason': f'Sample rate {sr}Hz below minimum {min_sr}Hz',
                'output_path': None
            }
        
        if sr == min_sr:
            # Resample from minimum to target
            action = 'resampled'
            reason = f'Resampled from {sr}Hz to {target_sr}Hz'
        elif sr == target_sr:
            # Copy as-is
            action = 'copied'
            reason = f'Sample rate already {target_sr}Hz'
        elif sr > target_sr:
            if downsample:
                # Downsample to target
                action = 'resampled'
                reason = f'Downsampled from {sr}Hz to {target_sr}Hz'
            else:
                return {
                    'action': 'skipped',
                    'reason': f'Sample rate {sr}Hz above target {target_sr}Hz (use --downsample to enable)',
                    'output_path': None
                }
        else:
            # Resample to target (between min and target)
            action = 'resampled'
            reason = f'Resampled from {sr}Hz to {target_sr}Hz'
        
        # Generate output filename
        output_filename = f"{filepath.stem}_{target_sr_k}k.wav"
        output_path = outdir / output_filename
        
        # Check if output exists
        if output_path.exists() and not overwrite:
            return {
                'action': 'skipped',
                'reason': f'Output file exists (use --overwrite to replace)',
                'output_path': output_path
            }
        
        # Process the file
        if action == 'copied':
            # Just copy the file
            import shutil
            outdir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(filepath, output_path)
        else:
            # Resample the file
            # Read audio
            audio_data, orig_sr = sf.read(str(filepath), dtype='float32')
            
            # Resample
            resampled_data = resample_to_target(audio_data, orig_sr, target_sr)
            
            # Write output
            outdir.mkdir(parents=True, exist_ok=True)
            sf.write(str(output_path), resampled_data.T if resampled_data.ndim > 1 else resampled_data, target_sr)
        
        logger.info(f"  → {action}: {reason}")
        return {
            'action': action,
            'reason': reason,
            'output_path': output_path
        }
        
    except Exception as e:
        logger.error(f"Error processing {filepath}: {e}")
        return {
            'action': 'error',
            'reason': str(e),
            'output_path': None
        }


def process_batch(input_path: Path, output_dir: Path, min_sr: int, target_sr: int, target_sr_k: float, downsample: bool = False, overwrite: bool = False) -> dict:
    """
    Process multiple WAV files in a directory, preserving folder structure.
    
    Args:
        input_path: Input file or directory
        output_dir: Output directory
        min_sr: Minimum sample rate threshold
        target_sr: Target sample rate for output
        target_sr_k: Target sample rate in kHz for naming
        downsample: Whether to downsample files with higher sample rates
        overwrite: Whether to overwrite existing output files
        
    Returns:
        Dictionary with batch processing statistics
    """
    # Collect WAV files
    if input_path.is_file():
        if input_path.suffix.lower() == '.wav':
            wav_files = [input_path]
        else:
            logger.error(f"Input file {input_path} is not a WAV file")
            return {'total': 0, 'processed': 0, 'skipped': 0, 'errors': 0}
    else:
        wav_files = list(input_path.rglob('*.wav'))
        if not wav_files:
            logger.error(f"No WAV files found in {input_path}")
            return {'total': 0, 'processed': 0, 'skipped': 0, 'errors': 0}
    
    logger.info(f"Found {len(wav_files)} WAV file(s) to process")
    
    # Process files
    stats = {'total': len(wav_files), 'processed': 0, 'skipped': 0, 'errors': 0}
    
    for wav_file in wav_files:
        # Calculate relative path to preserve folder structure
        if input_path.is_file():
            rel_path = Path(wav_file.name)
        else:
            rel_path = wav_file.relative_to(input_path)
        
        # Create output subdirectory
        file_output_dir = output_dir / rel_path.parent
        
        # Process file
        result = process_file(wav_file, file_output_dir, min_sr, target_sr, target_sr_k, downsample, overwrite)
        
        if result['action'] == 'error':
            stats['errors'] += 1
        elif result['action'] == 'skipped':
            stats['skipped'] += 1
        else:
            stats['processed'] += 1
    
    return stats
