# Enhance PDF Text Clarity

Convert PDF pages to high-clarity images with configurable sharpening filters. Ideal for improving readability of scanned documents or text-heavy PDFs.

## Features

- Configurable DPI output (default: 144)
- Unsharp mask sharpening with adjustable radius, percent, and threshold
- Multi-format output: PDF, PNG, JPEG
- Password-protected PDF support
- Multi-page handling with automatic page numbering for image outputs

## Requirements

- Python 3.10+
- PyMuPDF 1.26.0
- Pillow 11.2.1

## Installation

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
python enhance.py <source> <destination> [options]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `source` | Path to the input PDF file |
| `destination` | Path to the output file (`.pdf`, `.png`, or `.jpg`) |

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--dpi` | 144 | Output resolution in DPI |
| `--sharpen-radius` | 2.0 | Unsharp mask radius |
| `--sharpen-percent` | 150 | Sharpening strength percentage |
| `--sharpen-threshold` | 3 | Unsharp mask threshold |
| `--password` | None | Password for encrypted PDFs |
| `-q`, `--quiet` | — | Suppress progress output |
| `-v`, `--verbose` | — | Enable debug logging |

## Examples

**Basic usage:**
```bash
python enhance.py document.pdf output.pdf
```

**High-DPI output with aggressive sharpening:**
```bash
python enhance.py scan.pdf enhanced.png --dpi 300 --sharpen-percent 200
```

**Password-protected PDF:**
```bash
python enhance.py secure.pdf output.pdf --password "mypassword"
```

**Multi-page to individual PNGs:**
```bash
python enhance.py book.pdf pages/page_001.png --dpi 200
```

## Output Behavior

- **PDF**: All pages merged into a single multi-page PDF
- **PNG/JPEG (single page)**: One output file
- **PNG/JPEG (multi-page)**: Numbered files (e.g., `output_001.png`, `output_002.png`)

## License

MIT
