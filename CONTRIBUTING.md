# Contributing to SynthLang

Thank you for your interest in contributing to SynthLang! Here's how to get started.

## Development Setup

```bash
git clone https://github.com/synthlang/synthlang.git
cd synthlang
pip install -e .
```

## Running Tests

```bash
python -m unittest discover src/tests/
```

## Coding Standards

- Follow PEP 8 style guide
- Use type hints for all public functions
- Write tests for new features
- Keep functions focused and small
- Document public APIs with docstrings

## Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Reporting Issues

- Use clear, descriptive titles
- Include reproduction steps
- Provide expected vs actual behavior
- Include system information (OS, Python version)