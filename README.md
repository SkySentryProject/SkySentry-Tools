# SkySentry Tools

A collection of audio and signal processing utilities for drone and aerial data analysis.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://img.shields.io/badge/CI-Placeholder-blue.svg)](https://github.com/SkySentryProject/SkySentry-Tools/actions)
[![Code style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Codecov](https://img.shields.io/badge/Codecov-Placeholder-green.svg)](https://codecov.io/gh/SkySentryProject/SkySentry-Tools)

## Available Tools

### wav2mel
A neutral, parameterized CLI that converts WAV files to mel-log spectrograms and exports windowed NPY segments.

**Quick Start:**
```bash
pip install -e .
wav2mel ./audio.wav --out ./output --sr 44100 --n-mels 64 --win-seconds 1.0 --step-seconds 0.5 --png
```

[📖 **Full wav2mel Documentation**](tools/wav2mel/README.md)

## Installation

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/SkySentryProject/SkySentry-Tools.git
cd SkySentry-Tools

# Create virtual environment and install
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

### System Dependencies

**macOS:**
```bash
brew install libsndfile
```

**Ubuntu/Debian:**
```bash
sudo apt-get install libsndfile1
```

**Windows:**
The `soundfile` package should handle Windows dependencies automatically.

### Python Version Support

- Python 3.9 or higher required
- Tested on Python 3.9, 3.10, 3.11, 3.12

### Verify Installation

```bash
# Test the installation
wav2mel --help

# Run tests
pip install pytest
pytest tools/ -v
```

### Troubleshooting Installation

**"pip: command not found"**
```bash
# Use python3 -m pip instead
python3 -m pip install -e .
```

**"No module named 'soundfile'" or libsndfile errors:**
```bash
# macOS
brew install libsndfile

# Ubuntu/Debian
sudo apt-get install libsndfile1

# Windows - install Visual C++ Redistributable
```

**Virtual environment issues:**
```bash
# Create fresh environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

## Project Structure

```
SkySentry-Tools/
├── tools/                  # Individual tools
│   ├── wav2mel/           # WAV to mel-spectrogram conversion
│   └── [future-tools]/    # Additional tools will be added here
├── samples/               # Sample files for testing
├── pyproject.toml         # Package configuration
└── README.md             # This file
```

## Adding New Tools

To add a new tool to this repository:

1. Create a new directory under `tools/` with your tool name
2. Add the tool's CLI entry point to `pyproject.toml` under `[project.scripts]`
3. Create a README.md in the tool's directory with full documentation
4. Follow the same structure as `wav2mel/` for consistency

### Example: Adding a new tool called "audioprocess"

```bash
mkdir tools/audioprocess
mkdir tools/audioprocess/tests
touch tools/audioprocess/__init__.py
touch tools/audioprocess/cli.py
touch tools/audioprocess/processing.py
touch tools/audioprocess/README.md
```

Then update `pyproject.toml`:
```toml
[project.scripts]
wav2mel = "tools.wav2mel.cli:main"
audioprocess = "tools.audioprocess.cli:main"
```

## Testing

### Setup Testing Environment

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install pytest if not already installed
pip install pytest
```

### Run Tests

```bash
# Run all tests
pytest tools/ -v

# Run tests for specific tool
pytest tools/wav2mel/tests/ -v

# Run with coverage (optional)
pip install pytest-cov
pytest tools/ --cov=tools --cov-report=html
```

### Expected Test Output

```
============================= test session starts ==============================
platform darwin -- Python 3.13.7, pytest-8.4.2, pluggy-2.0.0
collected 1 item

tools/wav2mel/tests/test_smoke.py::test_segment_shapes PASSED    [100%]

============================== 1 passed in 3.98s ==============================
```

## Contributing

We welcome contributions! Please follow these guidelines:

### Code Style
- Use [Black](https://black.readthedocs.io/) for code formatting
- Follow PEP 8 conventions
- Add type hints for new functions

### Commit Messages
- Use conventional commits format (optional but preferred)
- Example: `feat: add support for HDF5 export`

### Pull Request Process
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Security & Privacy

- **No telemetry**: The tools do not collect or transmit any data
- **No embedded secrets**: All parameters must be provided explicitly via CLI
- **Local processing only**: All computation happens on your machine
- **No network access**: No external API calls or data transmission

## Compatibility

### Operating Systems
- **Linux**: Tested on Ubuntu 20.04+, CentOS 7+
- **macOS**: Tested on macOS 10.15+ (Intel and Apple Silicon)
- **Windows**: Tested on Windows 10/11 with Python 3.9+

### Terminal Encoding
- UTF-8 encoding recommended for international filenames
- Windows users may need to set `PYTHONIOENCODING=utf-8`

## Roadmap

Potential future tools (not committed):

- **Audio Analysis**: Spectral analysis, noise reduction, audio classification
- **Signal Processing**: Filtering, feature extraction, anomaly detection
- **Data Conversion**: Format conversion, batch processing, metadata extraction
- **Visualization**: Advanced plotting, interactive analysis, report generation

## Versioning & Changelog

This project follows [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH).

- **MAJOR**: Breaking changes to CLI interfaces or output formats
- **MINOR**: New tools or features, backward compatible
- **PATCH**: Bug fixes, backward compatible

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- **librosa**: Audio and music signal processing
- **soundfile**: Audio file I/O via libsndfile
- **NumPy/SciPy**: Numerical computing foundation
- **matplotlib**: Visualization capabilities
- **tqdm**: Progress bar implementation

---

*This toolkit is designed for research and development purposes. For production use, ensure appropriate testing and validation of your specific use case.*