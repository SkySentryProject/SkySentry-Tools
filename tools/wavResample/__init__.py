"""
WAV Resampler Tool

A professional tool for resampling WAV files to 48kHz with intelligent handling
of different input sample rates and batch processing capabilities.
"""

from .processing import detect_sr, resample_to_target, process_file

__version__ = "0.1.0"
__all__ = ["detect_sr", "resample_to_target", "process_file"]
