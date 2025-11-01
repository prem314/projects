#!/usr/bin/env python3
"""
embed_text_on_image.py

This script reads a text file and overlays its contents onto a dark wallpaper
image. It is designed to be robust enough to handle different text lengths
and automatically adjusts the font size so that the text fits nicely on the
image while leaving adequate margins on all sides. The script uses the
Python Imaging Library (Pillow) for image manipulation.

Usage:
    python embed_text_on_image.py --image INPUT_IMAGE_PATH \
        --text TEXT_FILE_PATH [--output OUTPUT_IMAGE_PATH]

If no output path is provided, the script will generate a filename based on
the input image, appending `_annotated` before the extension.

The text is rendered in white by default to provide good contrast against
dark backgrounds. A subtle drop shadow is added to enhance readability.
"""

import argparse
import os
import sys
import textwrap
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont


def load_font(target_height: int, font_path: str = None) -> ImageFont.FreeTypeFont:
    """Return a font object sized relative to the target height.

    If a custom font path is provided and exists, that font will be used.
    Otherwise, Pillow's default font is used. The initial font size is
    computed as a fraction of the image height; this size may be reduced
    later if the text does not fit.

    Args:
        target_height: The height of the image onto which text will be
            rendered.
        font_path: Optional path to a .ttf font file.

    Returns:
        A PIL ImageFont object.
    """
    # Start with a reasonably large font size relative to the image height.
    initial_size = max(12, target_height // 20)
    # Try to load a custom font if provided
    if font_path and os.path.exists(font_path):
        try:
            return ImageFont.truetype(font_path, initial_size)
        except Exception:
            pass
    # Try to load a common system font (DejaVuSans) which Pillow includes
    try:
        return ImageFont.truetype("DejaVuSans.ttf", initial_size)
    except Exception:
        # Fallback to PIL's default bitmap font; note that this font lacks size/path
        # information, so downstream code should handle missing attributes gracefully.
        return ImageFont.load_default()


def adjust_font_size(draw: ImageDraw.Draw, text_lines: list, font: ImageFont.FreeTypeFont,
                     max_width: int, max_height: int) -> ImageFont.FreeTypeFont:
    """Reduce the font size until the wrapped text fits within the available space.

    Args:
        draw: An ImageDraw object used to measure text.
        text_lines: A list of strings representing lines of text to render.
        font: The initial font to be adjusted.
        max_width: The maximum width allowed for the text block.
        max_height: The maximum height allowed for the text block.

    Returns:
        A new ImageFont object whose size ensures that the text fits within
        the given width and height constraints.
    """
    # Copy the font size to adjust it without modifying the original font directly.
    # Obtain starting font size; fallback to 20 if unknown
    font_size = getattr(font, "size", 20)
    # Obtain the underlying font file path if available
    font_path = getattr(font, "path", None)
    # If the font has no path attribute (e.g., bitmap default font), we cannot
    # scale it reliably; simply return the original font
    if font_path is None:
        return font
    while font_size > 10:  # Minimum sensible font size
        # Create a new font instance at this size
        try:
            new_font = ImageFont.truetype(font_path, font_size)
        except Exception:
            # If loading fails, break to avoid infinite loop
            break
        # Measure the maximum width and total height of all lines
        max_line_width = 0
        total_height = 0
        line_spacing = int(new_font.size * 0.2)  # 20% of font size as spacing
        for line in text_lines:
            bbox = draw.textbbox((0, 0), line, font=new_font)
            line_width = bbox[2] - bbox[0]
            line_height = bbox[3] - bbox[1]
            if line_width > max_line_width:
                max_line_width = line_width
            total_height += line_height + line_spacing
        # Remove the last added spacing
        total_height -= line_spacing if total_height > 0 else 0
        # Check if text fits within boundaries
        if max_line_width <= max_width and total_height <= max_height:
            return new_font
        # Reduce font size and try again
        font_size -= 1
    # Return the smallest font if nothing fits
    return new_font


def prepare_text(text: str, draw: ImageDraw.Draw, font: ImageFont.FreeTypeFont,
                 max_width: int) -> list:
    """Wrap each line of the text so that it fits within the given width.

    Args:
        text: The raw text content to wrap.
        draw: An ImageDraw object used to measure text.
        font: The current font used for measuring text width.
        max_width: The maximum width allowed for a line of text.

    Returns:
        A list of wrapped lines.
    """
    wrapped_lines = []
    for original_line in text.splitlines():
        # Use textwrap to wrap long lines
        if original_line.strip() == "":
            wrapped_lines.append("")
            continue
        words = original_line.split()
        current_line = ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if (bbox[2] - bbox[0]) <= max_width:
                current_line = test_line
            else:
                if current_line:
                    wrapped_lines.append(current_line)
                current_line = word
        if current_line:
            wrapped_lines.append(current_line)
    return wrapped_lines


def annotate_image(image_path: str, text_path: str, output_path: str, font_path: str = None) -> None:
    """Main function to load image, read text, and embed the text onto the image.

    Args:
        image_path: Path to the source wallpaper image.
        text_path: Path to the text file containing data to embed.
        output_path: Path where the annotated image should be saved.
        font_path: Optional path to a custom font file.
    """
    # Open the image
    image = Image.open(image_path).convert("RGB")
    width, height = image.size
    draw = ImageDraw.Draw(image)

    # Load and read text
    with open(text_path, "r", encoding="utf-8") as f:
        raw_text = f.read().strip()

    # Load initial font
    font = load_font(height, font_path)

    # Define margins as a percentage of image dimensions
    margin_x = int(width * 0.1)
    margin_y = int(height * 0.05)
    max_text_width = width - 2 * margin_x
    max_text_height = height - 2 * margin_y

    # Prepare wrapped text using the initial font
    wrapped_lines = prepare_text(raw_text, draw, font, max_text_width)
    # Adjust font size downwards until text fits
    font = adjust_font_size(draw, wrapped_lines, font, max_text_width, max_text_height)
    # Reduce font size slightly (10%) to leave breathing room if possible
    # Only adjust if the font has a path and size attribute
    base_path = getattr(font, "path", None)
    base_size = getattr(font, "size", None)
    if base_path and base_size:
        reduced_size = max(10, int(base_size * 0.9))
        try:
            font = ImageFont.truetype(base_path, reduced_size)
        except Exception:
            # If loading fails, retain original font
            pass
    # Re-wrap lines with the adjusted font
    wrapped_lines = prepare_text(raw_text, draw, font, max_text_width)

    # Recalculate total text height to vertically center within available space
    base_spacing = max(1, int(font.size * 0.2))
    line_heights = []
    for line in wrapped_lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_height = bbox[3] - bbox[1]
        line_heights.append(line_height)
    gap_spacings = []
    for idx in range(max(0, len(wrapped_lines) - 1)):
        spacing = base_spacing
        current = wrapped_lines[idx].strip().lower()
        next_line = wrapped_lines[idx + 1].strip().lower()
        if "blood group" in current:
            spacing += base_spacing
        if "address" in next_line:
            spacing += base_spacing
        gap_spacings.append(spacing)
    total_text_height = sum(line_heights) + sum(gap_spacings)

    # Determine starting Y coordinate; if text height fits, center within margins
    available_height = height - 2 * margin_y
    y_start = margin_y + (available_height - total_text_height) // 2 if total_text_height < available_height else margin_y

    # Draw each line with drop shadow for readability
    x_start = margin_x
    shadow_offset = max(1, font.size // 20)  # small offset relative to font size
    cumulative_offsets = []
    offset = 0
    for idx, line_height in enumerate(line_heights):
        cumulative_offsets.append(offset)
        offset += line_height
        if idx < len(gap_spacings):
            offset += gap_spacings[idx]
    for idx, (line, line_height) in enumerate(zip(wrapped_lines, line_heights)):
        y = y_start + cumulative_offsets[idx]
        # Draw drop shadow (semi-transparent black)
        if line.strip():
            draw.text((x_start + shadow_offset, y + shadow_offset), line, font=font, fill=(0, 0, 0, 255))
        # Draw main text in white
        draw.text((x_start, y), line, font=font, fill=(255, 255, 255, 255))

    # Save the annotated image
    image.save(output_path)


def derive_output_path(image_path: str, output_arg: str = None) -> str:
    """Construct a reasonable output filename based on input.

    If the user provides an explicit output path, use it. Otherwise, append
    `_annotated` before the file extension of the input image.
    """
    if output_arg:
        return output_arg
    base, ext = os.path.splitext(image_path)
    return f"{base}_annotated{ext}"


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Overlay text from a file onto a wallpaper image.")
    parser.add_argument("--image", required=True, help="Path to the input image (dark wallpaper).")
    parser.add_argument("--text", required=True, help="Path to the text file containing content to embed.")
    parser.add_argument("--output", default=None, help="Optional path for the output image.")
    parser.add_argument("--font", default=None, help="Optional path to a .ttf font to use.")
    return parser.parse_args()


def main():
    def _option_missing(option_name: str) -> bool:
        flag_with_equals = f"{option_name}="
        return all(
            arg != option_name and not arg.startswith(flag_with_equals)
            for arg in sys.argv[1:]
        )

    auto_args = []
    if _option_missing("--image"):
        jpg_files = sorted(
            entry for entry in os.listdir(".") if entry.lower().endswith(".jpg")
        )
        if not jpg_files:
            raise SystemExit("No .jpg files found in the current working directory.")
        auto_args.extend(["--image", jpg_files[0]])
    if _option_missing("--text"):
        txt_files = sorted(
            entry for entry in os.listdir(".") if entry.lower().endswith(".txt")
        )
        if not txt_files:
            raise SystemExit("No .txt files found in the current working directory.")
        auto_args.extend(["--text", txt_files[0]])
    if auto_args:
        sys.argv.extend(auto_args)

    args = parse_args()
    output_path = derive_output_path(args.image, args.output)
    annotate_image(args.image, args.text, output_path, args.font)
    print(f"Annotated image saved to: {output_path}")


if __name__ == "__main__":
    main()
