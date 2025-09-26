"""
Command-line interface for WAV resampling tool.

This module provides the CLI interface for the wavResample tool,
handling argument parsing and orchestrating batch processing.
"""

from pathlib import Path
import argparse
import sys
from tqdm import tqdm

from .processing import process_batch, DEFAULT_MIN_SAMPLE_RATE, DEFAULT_TARGET_SAMPLE_RATE, DEFAULT_TARGET_SAMPLE_RATE_K


def build_parser():
    """Build the command-line argument parser."""
    ap = argparse.ArgumentParser(
        prog="wavResample",
        description="Professional WAV resampling tool for converting audio files to target sample rate with intelligent sample rate handling."
    )
    
    ap.add_argument(
        "input", 
        type=str, 
        help="Input WAV file or directory containing WAV files"
    )
    
    ap.add_argument(
        "--output", 
        type=str, 
        default="./resampled_output", 
        help="Output directory (default: ./resampled_output)"
    )
    
    ap.add_argument(
        "--downsample", 
        action="store_true", 
        help="Enable downsampling of files with sample rates above 48kHz (default: False)"
    )
    
    ap.add_argument(
        "--overwrite", 
        action="store_true", 
        help="Overwrite existing output files (default: False)"
    )
    
    ap.add_argument(
        "--verbose", 
        action="store_true", 
        help="Enable verbose logging output"
    )
    
    ap.add_argument(
        "--min-sample-rate",
        type=int,
        default=DEFAULT_MIN_SAMPLE_RATE,
        help=f"Minimum sample rate threshold (default: {DEFAULT_MIN_SAMPLE_RATE}Hz)"
    )
    
    ap.add_argument(
        "--target-sample-rate",
        type=int,
        default=DEFAULT_TARGET_SAMPLE_RATE,
        help=f"Target sample rate for output (default: {DEFAULT_TARGET_SAMPLE_RATE}Hz)"
    )
    
    ap.add_argument(
        "--target-sample-rate-k",
        type=float,
        default=DEFAULT_TARGET_SAMPLE_RATE_K,
        help=f"Target sample rate in kHz for output filename (default: {DEFAULT_TARGET_SAMPLE_RATE_K}k)"
    )
    
    return ap


def main(argv=None):
    """Main entry point for the CLI."""
    ap = build_parser()
    args = ap.parse_args(argv)
    
    # Configure logging level
    import logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate input path
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input path '{input_path}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    # Validate output directory
    output_dir = Path(args.output)
    
    print(f"WAV Resampler - Processing audio files to {args.target_sample_rate}Hz")
    print(f"Input: {input_path.resolve()}")
    print(f"Output: {output_dir.resolve()}")
    print(f"Min sample rate: {args.min_sample_rate}Hz")
    print(f"Target sample rate: {args.target_sample_rate}Hz")
    print(f"Downsample enabled: {args.downsample}")
    print(f"Overwrite existing: {args.overwrite}")
    print("-" * 60)
    
    try:
        # Process files
        stats = process_batch(input_path, output_dir, args.min_sample_rate, args.target_sample_rate, args.target_sample_rate_k, args.downsample, args.overwrite)
        
        # Print summary
        print("-" * 60)
        print("Processing Summary:")
        print(f"  Total files: {stats['total']}")
        print(f"  Processed: {stats['processed']}")
        print(f"  Skipped: {stats['skipped']}")
        print(f"  Errors: {stats['errors']}")
        
        if stats['errors'] > 0:
            print(f"\nWarning: {stats['errors']} file(s) had errors during processing")
            sys.exit(1)
        else:
            print(f"\nSuccess! All files processed successfully.")
            print(f"Results saved to: {output_dir.resolve()}")
            
    except KeyboardInterrupt:
        print("\nProcessing interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
