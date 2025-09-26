"""
Unit tests for the wavResample tool.

Tests core functionality including sample rate detection, resampling,
and file processing with various scenarios.
"""

import pytest
import numpy as np
import soundfile as sf
from pathlib import Path
import tempfile
import shutil

from ..processing import detect_sr, resample_to_target, process_file, process_batch, DEFAULT_MIN_SAMPLE_RATE, DEFAULT_TARGET_SAMPLE_RATE, DEFAULT_TARGET_SAMPLE_RATE_K


class TestDetectSR:
    """Test sample rate detection functionality."""
    
    def test_detect_sr_valid_file(self):
        """Test detecting sample rate from a valid WAV file."""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            # Create a test WAV file with 22050Hz sample rate
            test_audio = np.random.randn(1000).astype(np.float32)
            sf.write(tmp.name, test_audio, 22050)
            
            try:
                sr = detect_sr(Path(tmp.name))
                assert sr == 22050
            finally:
                Path(tmp.name).unlink()
    
    def test_detect_sr_nonexistent_file(self):
        """Test error handling for non-existent file."""
        with pytest.raises(RuntimeError, match="Failed to read audio file"):
            detect_sr(Path("nonexistent.wav"))


class TestResampleToTarget:
    """Test resampling functionality."""
    
    def test_resample_mono_22k_to_44k(self):
        """Test resampling mono audio from 22kHz to 44.1kHz."""
        # Create test audio
        duration = 1.0  # 1 second
        orig_sr = 22050
        target_sr = 44100
        
        # Generate test signal
        t = np.linspace(0, duration, int(orig_sr * duration))
        test_audio = np.sin(2 * np.pi * 440 * t).astype(np.float32)  # 440Hz tone
        
        # Resample
        resampled = resample_to_target(test_audio, orig_sr, target_sr)
        
        # Check output properties
        assert resampled.ndim == 1  # Should remain mono
        assert len(resampled) == int(target_sr * duration)  # Correct length
        assert resampled.dtype == np.float32  # Preserve dtype
    
    def test_resample_stereo_22k_to_44k(self):
        """Test resampling stereo audio from 22kHz to 44.1kHz."""
        # Create test stereo audio
        duration = 0.5  # 0.5 seconds
        orig_sr = 22050
        target_sr = 44100
        
        # Generate test stereo signal
        t = np.linspace(0, duration, int(orig_sr * duration))
        left_channel = np.sin(2 * np.pi * 440 * t).astype(np.float32)
        right_channel = np.sin(2 * np.pi * 880 * t).astype(np.float32)
        test_audio = np.stack([left_channel, right_channel], axis=0)
        
        # Resample
        resampled = resample_to_target(test_audio, orig_sr, target_sr)
        
        # Check output properties
        assert resampled.ndim == 2  # Should remain stereo
        assert resampled.shape[0] == 2  # Two channels
        assert resampled.shape[1] == int(target_sr * duration)  # Correct length
        assert resampled.dtype == np.float32  # Preserve dtype
    
    def test_resample_already_target(self):
        """Test that audio at target sample rate is returned unchanged."""
        test_audio = np.random.randn(1000).astype(np.float32)
        resampled = resample_to_target(test_audio, 44100, 44100)
        
        np.testing.assert_array_equal(resampled, test_audio)
    
    def test_resample_invalid_sr(self):
        """Test error handling for invalid sample rate."""
        test_audio = np.random.randn(1000).astype(np.float32)
        
        with pytest.raises(ValueError, match="Invalid sample rate"):
            resample_to_target(test_audio, 0, 44100)
        
        with pytest.raises(ValueError, match="Invalid sample rate"):
            resample_to_target(test_audio, -1, 44100)


class TestProcessFile:
    """Test file processing functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.output_dir = self.temp_dir / "output"
        self.output_dir.mkdir()
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def create_test_wav(self, filename: str, sample_rate: int, duration: float = 0.1) -> Path:
        """Create a test WAV file."""
        filepath = self.temp_dir / filename
        test_audio = np.random.randn(int(sample_rate * duration)).astype(np.float32)
        sf.write(str(filepath), test_audio, sample_rate)
        return filepath
    
    def test_process_file_16k_to_44k(self):
        """Test processing 16kHz file (should be resampled)."""
        input_file = self.create_test_wav("test_16k.wav", 16000)
        
        result = process_file(input_file, self.output_dir, DEFAULT_MIN_SAMPLE_RATE, DEFAULT_TARGET_SAMPLE_RATE, DEFAULT_TARGET_SAMPLE_RATE_K, downsample=False, overwrite=False)
        
        assert result['action'] == 'resampled'
        assert 'Resampled from 16000Hz to 44100Hz' in result['reason']
        assert result['output_path'] is not None
        assert result['output_path'].name == "test_16k_44.1k.wav"
        
        # Verify output file exists and has correct sample rate
        assert result['output_path'].exists()
        output_sr = detect_sr(result['output_path'])
        assert output_sr == 44100
    
    def test_process_file_44k_copy(self):
        """Test processing 44.1kHz file (should be copied)."""
        input_file = self.create_test_wav("test_44k.wav", 44100)
        
        result = process_file(input_file, self.output_dir, DEFAULT_MIN_SAMPLE_RATE, DEFAULT_TARGET_SAMPLE_RATE, DEFAULT_TARGET_SAMPLE_RATE_K, downsample=False, overwrite=False)
        
        assert result['action'] == 'copied'
        assert 'Sample rate already 44100Hz' in result['reason']
        assert result['output_path'] is not None
        assert result['output_path'].name == "test_44k_44.1k.wav"
        
        # Verify output file exists
        assert result['output_path'].exists()
    
    def test_process_file_96k_skip(self):
        """Test processing 96kHz file without downsampling (should be skipped)."""
        input_file = self.create_test_wav("test_96k.wav", 96000)
        
        result = process_file(input_file, self.output_dir, DEFAULT_MIN_SAMPLE_RATE, DEFAULT_TARGET_SAMPLE_RATE, DEFAULT_TARGET_SAMPLE_RATE_K, downsample=False, overwrite=False)
        
        assert result['action'] == 'skipped'
        assert 'use --downsample to enable' in result['reason']
        assert result['output_path'] is None
    
    def test_process_file_96k_downsample(self):
        """Test processing 96kHz file with downsampling enabled."""
        input_file = self.create_test_wav("test_96k.wav", 96000)
        
        result = process_file(input_file, self.output_dir, DEFAULT_MIN_SAMPLE_RATE, DEFAULT_TARGET_SAMPLE_RATE, DEFAULT_TARGET_SAMPLE_RATE_K, downsample=True, overwrite=False)
        
        assert result['action'] == 'resampled'
        assert 'Downsampled from 96000Hz to 44100Hz' in result['reason']
        assert result['output_path'] is not None
        assert result['output_path'].name == "test_96k_44.1k.wav"
        
        # Verify output file exists and has correct sample rate
        assert result['output_path'].exists()
        output_sr = detect_sr(result['output_path'])
        assert output_sr == 44100
    
    def test_process_file_too_low_sr(self):
        """Test processing file with sample rate below minimum (should be skipped)."""
        input_file = self.create_test_wav("test_8k.wav", 8000)
        
        result = process_file(input_file, self.output_dir, DEFAULT_MIN_SAMPLE_RATE, DEFAULT_TARGET_SAMPLE_RATE, DEFAULT_TARGET_SAMPLE_RATE_K, downsample=False, overwrite=False)
        
        assert result['action'] == 'skipped'
        assert 'Sample rate 8000Hz below minimum 16000Hz' in result['reason']
        assert result['output_path'] is None
    
    def test_process_file_overwrite(self):
        """Test overwrite functionality."""
        input_file = self.create_test_wav("test_22k.wav", 22050)
        
        # Process first time
        result1 = process_file(input_file, self.output_dir, DEFAULT_MIN_SAMPLE_RATE, DEFAULT_TARGET_SAMPLE_RATE, DEFAULT_TARGET_SAMPLE_RATE_K, downsample=False, overwrite=False)
        assert result1['action'] == 'resampled'
        assert result1['output_path'].exists()
        
        # Process second time without overwrite (should be skipped)
        result2 = process_file(input_file, self.output_dir, DEFAULT_MIN_SAMPLE_RATE, DEFAULT_TARGET_SAMPLE_RATE, DEFAULT_TARGET_SAMPLE_RATE_K, downsample=False, overwrite=False)
        assert result2['action'] == 'skipped'
        assert 'Output file exists' in result2['reason']
        
        # Process third time with overwrite (should succeed)
        result3 = process_file(input_file, self.output_dir, DEFAULT_MIN_SAMPLE_RATE, DEFAULT_TARGET_SAMPLE_RATE, DEFAULT_TARGET_SAMPLE_RATE_K, downsample=False, overwrite=True)
        assert result3['action'] == 'resampled'
        assert result3['output_path'].exists()


class TestProcessBatch:
    """Test batch processing functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.output_dir = self.temp_dir / "output"
        self.input_dir = self.temp_dir / "input"
        self.input_dir.mkdir()
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def create_test_wav(self, filepath: Path, sample_rate: int, duration: float = 0.1):
        """Create a test WAV file."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        test_audio = np.random.randn(int(sample_rate * duration)).astype(np.float32)
        sf.write(str(filepath), test_audio, sample_rate)
    
    def test_process_batch_single_file(self):
        """Test batch processing with a single file."""
        input_file = self.input_dir / "test_22k.wav"
        self.create_test_wav(input_file, 22050)
        
        stats = process_batch(input_file, self.output_dir, DEFAULT_MIN_SAMPLE_RATE, DEFAULT_TARGET_SAMPLE_RATE, DEFAULT_TARGET_SAMPLE_RATE_K, downsample=False, overwrite=False)
        
        assert stats['total'] == 1
        assert stats['processed'] == 1
        assert stats['skipped'] == 0
        assert stats['errors'] == 0
    
    def test_process_batch_directory(self):
        """Test batch processing with multiple files in directory."""
        # Create test files with different sample rates
        files = [
            ("file_16k.wav", 16000),  # Should be resampled
            ("file_44k.wav", 44100),  # Should be copied
            ("file_96k.wav", 96000),  # Should be skipped (no downsampling)
        ]
        
        for filename, sr in files:
            filepath = self.input_dir / filename
            self.create_test_wav(filepath, sr)
        
        stats = process_batch(self.input_dir, self.output_dir, DEFAULT_MIN_SAMPLE_RATE, DEFAULT_TARGET_SAMPLE_RATE, DEFAULT_TARGET_SAMPLE_RATE_K, downsample=False, overwrite=False)
        
        assert stats['total'] == 3
        assert stats['processed'] == 2  # 16k and 44k files
        assert stats['skipped'] == 1    # 96k file
        assert stats['errors'] == 0
    
    def test_process_batch_with_downsampling(self):
        """Test batch processing with downsampling enabled."""
        # Create test files
        files = [
            ("file_16k.wav", 16000),  # Should be resampled
            ("file_44k.wav", 44100),  # Should be copied
            ("file_96k.wav", 96000),  # Should be downsampled
        ]
        
        for filename, sr in files:
            filepath = self.input_dir / filename
            self.create_test_wav(filepath, sr)
        
        stats = process_batch(self.input_dir, self.output_dir, DEFAULT_MIN_SAMPLE_RATE, DEFAULT_TARGET_SAMPLE_RATE, DEFAULT_TARGET_SAMPLE_RATE_K, downsample=True, overwrite=False)
        
        assert stats['total'] == 3
        assert stats['processed'] == 3  # All files processed
        assert stats['skipped'] == 0
        assert stats['errors'] == 0
    
    def test_process_batch_folder_structure(self):
        """Test that folder structure is preserved during batch processing."""
        # Create nested folder structure
        subdir = self.input_dir / "subfolder"
        subdir.mkdir()
        
        files = [
            (self.input_dir / "root_file.wav", 22050),
            (subdir / "sub_file.wav", 44100),
        ]
        
        for filepath, sr in files:
            self.create_test_wav(filepath, sr)
        
        stats = process_batch(self.input_dir, self.output_dir, DEFAULT_MIN_SAMPLE_RATE, DEFAULT_TARGET_SAMPLE_RATE, DEFAULT_TARGET_SAMPLE_RATE_K, downsample=False, overwrite=False)
        
        assert stats['total'] == 2
        assert stats['processed'] == 2
        assert stats['errors'] == 0
        
        # Check that folder structure is preserved
        assert (self.output_dir / "root_file_44.1k.wav").exists()
        assert (self.output_dir / "subfolder" / "sub_file_44.1k.wav").exists()
    
    def test_process_batch_no_wav_files(self):
        """Test batch processing with no WAV files."""
        # Create a non-WAV file
        txt_file = self.input_dir / "test.txt"
        txt_file.write_text("This is not a WAV file")
        
        stats = process_batch(self.input_dir, self.output_dir, DEFAULT_MIN_SAMPLE_RATE, DEFAULT_TARGET_SAMPLE_RATE, DEFAULT_TARGET_SAMPLE_RATE_K, downsample=False, overwrite=False)
        
        assert stats['total'] == 0
        assert stats['processed'] == 0
        assert stats['skipped'] == 0
        assert stats['errors'] == 0


def test_smoke():
    """Smoke test to verify basic functionality."""
    # This is a simple test to ensure the module can be imported and basic functions work
    from ..processing import detect_sr, resample_to_target, process_file
    
    # Test that functions are callable
    assert callable(detect_sr)
    assert callable(resample_to_target)
    assert callable(process_file)
    
    # Test resampling with simple data
    test_audio = np.random.randn(1000).astype(np.float32)
    resampled = resample_to_target(test_audio, 22050, 44100)
    assert len(resampled) > 0
    assert resampled.dtype == np.float32
