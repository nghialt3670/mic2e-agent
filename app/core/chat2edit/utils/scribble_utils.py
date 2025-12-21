from typing import List, Tuple

import svgpathtools
from PIL import Image as PILImage, ImageDraw

from app.core.chat2edit.models.image import Image
from app.core.chat2edit.models.scribble import Scribble


def _convert_path_commands_to_svg_string(path_commands: List) -> str:
    """Convert list of path commands to SVG path string."""
    path_parts = []
    for command in path_commands:
        if not command or len(command) < 1:
            continue
        cmd_type = str(command[0]).upper()
        coords = [str(c) for c in command[1:]]
        path_parts.append(f"{cmd_type} {' '.join(coords)}")
    return " ".join(path_parts)


def _sample_path_points(
    path_string: str, num_samples: int = 500
) -> List[Tuple[float, float]]:
    """Sample points from an SVG path string using svgpathtools."""
    try:
        # Parse the SVG path
        paths = svgpathtools.parse_path(path_string)

        if not paths or len(paths) == 0:
            return []

        # Sample points along the path
        points = []
        path_length = paths.length()

        if path_length == 0:
            return []

        # Sample points evenly along the path
        for i in range(num_samples):
            t = i / (num_samples - 1) if num_samples > 1 else 0
            try:
                point = paths.point(t)
                # Convert complex number to tuple (real, imag)
                points.append((point.real, point.imag))
            except (ValueError, ZeroDivisionError):
                # Skip invalid points
                continue

        return points
    except Exception as e:
        # Fallback to empty list if parsing fails
        print(f"Warning: Failed to parse SVG path: {e}")
        return []


def convert_scribble_to_mask_image(scribble: Scribble, image: Image) -> PILImage.Image:
    """Convert a scribble path to a binary mask image using svgpathtools.

    Args:
        scribble: Scribble object containing path data and stroke properties
        image: Image object to get dimensions from

    Returns:
        PIL Image in 'L' mode (grayscale) where white (255) represents the scribble
    """
    image_pil = image.get_image()
    img_width, img_height = image_pil.size
    mask = PILImage.new("L", (img_width, img_height), 0)

    path_data = scribble.path
    if not path_data:
        return mask
    if isinstance(path_data, str) and not path_data.strip():
        return mask
    if isinstance(path_data, list) and len(path_data) == 0:
        return mask

    # Convert path data to SVG string if needed
    if isinstance(path_data, list):
        path_string = _convert_path_commands_to_svg_string(path_data)
    else:
        path_string = path_data

    if not path_string.strip():
        return mask

    # Sample points from the SVG path using svgpathtools
    sampled_points = _sample_path_points(path_string, num_samples=500)

    if len(sampled_points) < 2:
        return mask

    # Path coordinates from Fabric.js are already in image pixel coordinates
    # where (0,0) is at top-left of the image, no transformation needed
    # Just clamp to image bounds
    transformed_points = []
    for x, y in sampled_points:
        img_x = int(x)
        img_y = int(y)
        # Clamp to image bounds
        img_x = max(0, min(img_x, img_width - 1))
        img_y = max(0, min(img_y, img_height - 1))
        transformed_points.append((img_x, img_y))

    if len(transformed_points) < 2:
        return mask

    # Draw the path on the mask
    draw = ImageDraw.Draw(mask)
    stroke_width = max(3, int(scribble.strokeWidth or 10))

    # Draw lines between consecutive points
    for i in range(len(transformed_points) - 1):
        draw.line(
            [transformed_points[i], transformed_points[i + 1]],
            fill=255,
            width=stroke_width,
        )

    # Draw circles at each point for smooth appearance
    point_radius = max(2, stroke_width // 2)
    for x, y in transformed_points:
        bbox = [
            x - point_radius,
            y - point_radius,
            x + point_radius,
            y + point_radius,
        ]
        draw.ellipse(bbox, fill=255)

    return mask
