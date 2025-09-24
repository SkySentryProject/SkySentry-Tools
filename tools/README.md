# SkySentry Tools Directory

This directory contains individual tools for audio and signal processing.

## Directory Structure

```
tools/
├── __init__.py          # Main tools package
├── wav2mel/            # WAV to mel-spectrogram conversion tool
│   ├── __init__.py
│   ├── cli.py          # Command-line interface
│   ├── processing.py   # Core processing functions
│   ├── README.md       # Tool-specific documentation
│   └── tests/          # Tool-specific tests
└── [future-tool]/      # Future tools will be added here
    ├── __init__.py
    ├── cli.py
    ├── processing.py
    ├── README.md
    └── tests/
```

## Available Tools

### wav2mel
WAV to mel-spectrogram conversion with windowed NPY segments.

- **CLI Command**: `wav2mel`
- **Documentation**: [wav2mel/README.md](wav2mel/README.md)
- **Features**: Full parameterization, multiple output formats, dataset-ready segments

## Adding New Tools

To add a new tool to this repository:

1. **Create tool directory structure**:
   ```bash
   mkdir tools/new-tool
   mkdir tools/new-tool/tests
   touch tools/new-tool/__init__.py
   touch tools/new-tool/cli.py
   touch tools/new-tool/processing.py
   touch tools/new-tool/README.md
   ```

2. **Add CLI entry point** to `pyproject.toml`:
   ```toml
   [project.scripts]
   wav2mel = "tools.wav2mel.cli:main"
   new-tool = "tools.new-tool.cli:main"
   ```

3. **Update main README**: Add your tool to the "Available Tools" section in the root README.md

4. **Create tool documentation**: Write comprehensive documentation in `tools/new-tool/README.md`

5. **Add tests**: Create test files in `tools/new-tool/tests/`

### Tool Development Guidelines

- **Consistent structure**: Follow the same directory layout as `wav2mel/`
- **CLI interface**: Use argparse for command-line arguments
- **Error handling**: Provide clear error messages and exit codes
- **Documentation**: Include full documentation with examples
- **Testing**: Add unit tests for core functionality
- **Type hints**: Use type hints for better code maintainability

### Example Tool Structure

```python
# tools/new-tool/cli.py
import argparse
from .processing import process_data

def build_parser():
    ap = argparse.ArgumentParser(
        prog="new-tool",
        description="Description of what the tool does"
    )
    ap.add_argument("input", help="Input file or directory")
    ap.add_argument("--out", default="./out", help="Output directory")
    # Add more arguments as needed
    return ap

def main(argv=None):
    ap = build_parser()
    args = ap.parse_args(argv)
    # Process arguments and call processing functions
    process_data(args.input, args.out, args)
```

## Shared Dependencies

All tools share common dependencies defined in the root `pyproject.toml`:
- numpy, scipy, soundfile, librosa, matplotlib, tqdm

If a tool needs additional dependencies, add them to the root `pyproject.toml` dependencies list.

## Testing

Run tests for all tools:
```bash
pytest tools/ -v
```

Run tests for a specific tool:
```bash
pytest tools/wav2mel/tests/ -v
```

## Code Style

- Use [Black](https://black.readthedocs.io/) for code formatting
- Follow PEP 8 conventions
- Add type hints for function parameters and return values
- Include docstrings for all public functions and classes
