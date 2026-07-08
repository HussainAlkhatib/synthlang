# CLI Tool - Text Statistics

A production-ready CLI tool that processes text files and outputs statistics. (v1.1.0)

## Description

This tool accepts command-line arguments to read a text file and compute statistics (word count, line count, character count).

## Usage

```bash
slang run cli1/cli1.sl --input input.txt --output out.txt
slang run cli1/cli1.sl --input input.txt --help
```

## Options

- `--input <file>`: Input text file to process
- `--output <file>`: Output file for results (optional, defaults to stdout)
- `--help`: Show usage information

## Examples

```bash
# Count words in a file and print to stdout
slang run cli1/cli1.sl --input sample.txt

# Save results to output file
slang run cli1/cli1.sl --input sample.txt --output stats.txt

# Show help
slang run cli1/cli1.sl --help
```