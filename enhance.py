#!/usr/bin/env python3
"""
PDF Text Clarity Enhancer

Converts PDF pages to images with sharpening applied to improve text clarity.
Supports configurable DPI, sharpening parameters, and multiple output formats.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

import fitz  # PyMuPDF
from PIL import Image, ImageFilter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Enhance PDF text clarity by applying sharpening filters.'
    )
    parser.add_argument(
        'source',
        type=str,
        help='Path to the source PDF file'
    )
    parser.add_argument(
        'destination',
        type=str,
        help='Path to the output file (PDF, PNG, or JPEG)'
    )
    parser.add_argument(
        '--dpi',
        type=int,
        default=144,
        help='Output DPI (default: 144)'
    )
    parser.add_argument(
        '--sharpen-radius',
        type=float,
        default=2.0,
        help='Unsharp mask radius (default: 2.0)'
    )
    parser.add_argument(
        '--sharpen-percent',
        type=int,
        default=150,
        help='Unsharp mask strength percentage (default: 150)'
    )
    parser.add_argument(
        '--sharpen-threshold',
        type=int,
        default=3,
        help='Unsharp mask threshold (default: 3)'
    )
    parser.add_argument(
        '--password',
        type=str,
        default=None,
        help='Password for encrypted PDFs'
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Suppress progress output'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    return parser.parse_args()


def validate_source(source_path: Path) -> None:
    """Validate that the source file exists and is a valid PDF."""
    if not source_path.exists():
        raise FileNotFoundError(f'Source file "{source_path}" does not exist')
    if not source_path.is_file():
        raise ValueError(f'Source "{source_path}" is not a file')
    if source_path.suffix.lower() != '.pdf':
        logger.warning(f'Source file "{source_path}" does not have a .pdf extension')


def get_output_format(destination: Path) -> str:
    """Determine output format from file extension."""
    suffix = destination.suffix.lower()
    format_map = {
        '.pdf': 'PDF',
        '.png': 'PNG',
        '.jpg': 'JPEG',
        '.jpeg': 'JPEG'
    }
    if suffix not in format_map:
        raise ValueError(
            f'Unsupported output format "{suffix}". '
            f'Supported formats: .pdf, .png, .jpg, .jpeg'
        )
    return format_map[suffix]


def render_pages_to_images(
    doc: fitz.Document,
    dpi: int,
    sharpen_radius: float,
    sharpen_percent: int,
    sharpen_threshold: int,
    quiet: bool = False
) -> List[Image.Image]:
    """Render all pages of a PDF to images with sharpening applied."""
    images: List[Image.Image] = []
    total_pages = len(doc)
    
    # Calculate scale factor from DPI (72 DPI is PDF native)
    scale = dpi / 72.0
    matrix = fitz.Matrix(scale, scale)
    
    unsharp_filter = ImageFilter.UnsharpMask(
        radius=sharpen_radius,
        percent=sharpen_percent,
        threshold=sharpen_threshold
    )
    
    for page_num, page in enumerate(doc, start=1):
        if not quiet:
            logger.info(f'Processing page {page_num}/{total_pages}')
        
        try:
            # Render page to pixmap
            pix = page.get_pixmap(matrix=matrix)
            
            # Convert to PIL Image
            if pix.alpha:
                # Handle transparency by compositing on white background
                img = Image.frombytes('RGBA', [pix.width, pix.height], pix.samples)
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            else:
                img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
            
            # Apply sharpening
            img = img.filter(unsharp_filter)
            images.append(img)
            
        except Exception as e:
            logger.error(f'Failed to render page {page_num}: {e}')
            raise
    
    return images


def save_images(
    images: List[Image.Image],
    destination: Path,
    output_format: str,
    dpi: int
) -> None:
    """Save processed images to the destination file."""
    if not images:
        raise ValueError('No images to save')
    
    save_kwargs: dict = {
        'resolution': dpi
    }
    
    if output_format == 'PDF':
        save_kwargs['save_all'] = True
        save_kwargs['append_images'] = images[1:]
        images[0].save(destination, **save_kwargs)
    elif output_format == 'PNG':
        if len(images) == 1:
            images[0].save(destination, **save_kwargs)
        else:
            # Save each page as a separate PNG with numbered suffix
            base = destination.stem
            stem_dir = destination.parent
            for i, img in enumerate(images, start=1):
                if len(images) > 1:
                    output_path = stem_dir / f'{base}_{i:03d}.png'
                else:
                    output_path = destination
                img.save(output_path, **save_kwargs)
                logger.info(f'Saved {output_path}')
    elif output_format == 'JPEG':
        save_kwargs['quality'] = 95
        if len(images) == 1:
            images[0].save(destination, **save_kwargs)
        else:
            # Save each page as a separate JPEG with numbered suffix
            base = destination.stem
            stem_dir = destination.parent
            for i, img in enumerate(images, start=1):
                if len(images) > 1:
                    output_path = stem_dir / f'{base}_{i:03d}.jpg'
                else:
                    output_path = destination
                img.save(output_path, **save_kwargs)
                logger.info(f'Saved {output_path}')


def enhance_pdf(
    source: Path,
    destination: Path,
    dpi: int = 144,
    sharpen_radius: float = 2.0,
    sharpen_percent: int = 150,
    sharpen_threshold: int = 3,
    password: Optional[str] = None,
    quiet: bool = False
) -> None:
    """
    Main function to enhance a PDF by applying sharpening to each page.
    
    Args:
        source: Path to the source PDF file
        destination: Path to the output file
        dpi: Output DPI (default: 144)
        sharpen_radius: Unsharp mask radius (default: 2.0)
        sharpen_percent: Unsharp mask strength percentage (default: 150)
        sharpen_threshold: Unsharp mask threshold (default: 3)
        password: Password for encrypted PDFs (optional)
        quiet: Suppress progress output (default: False)
    """
    validate_source(source)
    output_format = get_output_format(destination)
    
    if not quiet:
        logger.info(f'Opening {source}...')
    
    try:
        doc = fitz.open(source)
        
        # Handle password-protected PDFs
        if doc.is_encrypted:
            if password:
                if not doc.authenticate(password):
                    raise ValueError('Invalid password for encrypted PDF')
                if not quiet:
                    logger.info('PDF authenticated successfully')
            else:
                raise ValueError(
                    'PDF is encrypted. Please provide a password using --password'
                )
        
        if len(doc) == 0:
            raise ValueError('PDF contains no pages')
        
        if not quiet:
            logger.info(f'Found {len(doc)} page(s), processing...')
        
        images = render_pages_to_images(
            doc,
            dpi=dpi,
            sharpen_radius=sharpen_radius,
            sharpen_percent=sharpen_percent,
            sharpen_threshold=sharpen_threshold,
            quiet=quiet
        )
        
        doc.close()
        
        if not quiet:
            logger.info(f'Saving to {destination}...')
        
        save_images(images, destination, output_format, dpi)
        
        if not quiet:
            logger.info(f'Done! Enhanced PDF saved to {destination}')
            
    except fitz.FileDataError as e:
        raise ValueError(f'Invalid or corrupted PDF file: {e}')
    except Exception as e:
        raise


def main() -> int:
    """Main entry point."""
    args = parse_arguments()
    
    # Set logging level based on verbosity flags
    if args.quiet:
        logger.setLevel(logging.ERROR)
    elif args.verbose:
        logger.setLevel(logging.DEBUG)
    
    source = Path(args.source)
    destination = Path(args.destination)
    
    # Create destination directory if it doesn't exist
    destination.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        enhance_pdf(
            source=source,
            destination=destination,
            dpi=args.dpi,
            sharpen_radius=args.sharpen_radius,
            sharpen_percent=args.sharpen_percent,
            sharpen_threshold=args.sharpen_threshold,
            password=args.password,
            quiet=args.quiet
        )
        return 0
    except FileNotFoundError as e:
        logger.error(e)
        return 1
    except ValueError as e:
        logger.error(e)
        return 1
    except Exception as e:
        logger.error(f'Unexpected error: {e}')
        return 1


if __name__ == '__main__':
    sys.exit(main())
