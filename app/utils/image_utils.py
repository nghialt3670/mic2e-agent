import base64
import io
import re
from typing import List, Tuple

import numpy as np
from PIL import Image
from scipy.ndimage import binary_dilation


def convert_ndarray_to_mask_image(image: np.ndarray) -> Image.Image:
    if image.ndim == 3:
        image = image.squeeze(0)
    image = (image * 255).astype(np.uint8)
    return Image.fromarray(image)


def get_bbox_from_mask_image(mask_image: Image.Image) -> Tuple[int, int, int, int]:
    mask = np.array(mask_image)
    y, x = np.where(mask)
    return min(x), min(y), max(x), max(y)


def convert_normalized_center_to_absolute_corners(
    cx: float, cy: float, box_w: float, box_h: float, img_w: int, img_h: int
) -> Tuple[int, int, int, int]:
    xmin = int((cx - box_w / 2) * img_w)
    ymin = int((cy - box_h / 2) * img_h)
    xmax = int((cx + box_w / 2) * img_w)
    ymax = int((cy + box_h / 2) * img_h)
    return xmin, ymin, xmax, ymax


def expand_mask_image(mask_image: Image.Image, iterations: int = 10) -> Image.Image:
    mask_array = np.array(mask_image)
    binary_mask = (mask_array > 127).astype(np.uint8)
    expanded_mask = binary_dilation(binary_mask, iterations=iterations).astype(np.uint8)
    expanded_mask = expanded_mask * 255
    return Image.fromarray(expanded_mask)


def convert_image_to_data_url(image: Image.Image) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    png_bytes = buffer.read()
    return f"data:image/png;base64,{base64.b64encode(png_bytes).decode('utf-8')}"


def convert_data_url_to_image(data_url: str) -> Image.Image:
    match = re.search(r"data:image/(.*?);base64,(.*)", data_url)
    if not match:
        raise ValueError("Invalid data URL")

    image_data = base64.b64decode(match.group(2))
    return Image.open(io.BytesIO(image_data))


def expand_mask_image(mask_image: Image.Image, iterations: int = 10) -> Image.Image:
    mask_array = np.array(mask_image)
    binary_mask = (mask_array > 127).astype(np.uint8)
    expanded_mask = binary_dilation(binary_mask, iterations=iterations).astype(np.uint8)
    expanded_mask = expanded_mask * 255
    return Image.fromarray(expanded_mask)


def extract_masked_region(
    original_image: Image.Image,
    mask: Image.Image,
    bbox: Tuple[int, int, int, int],
) -> Image.Image:
    """Extract the masked region from the original image and crop to bounding box.

    Args:
        original_image: The original full-size image
        mask: The binary mask (full image size, L mode)
        bbox: Bounding box (x1, y1, x2, y2)

    Returns:
        Cropped image with only the masked region visible
    """
    # Ensure original image is RGB/RGBA
    if original_image.mode not in ("RGB", "RGBA"):
        original_image = original_image.convert("RGB")

    # Convert mask to binary (0 or 255)
    if mask.mode != "L":
        mask = mask.convert("L")

    # Create a copy of the original image
    masked_image = original_image.copy()

    # Apply mask: set pixels outside mask to transparent/black
    if masked_image.mode == "RGB":
        masked_image = masked_image.convert("RGBA")

    # Convert mask to numpy array for processing
    mask_array = np.array(mask)
    # Normalize mask to 0-1 range
    mask_array = (mask_array > 127).astype(np.uint8)

    # Apply mask to alpha channel
    img_array = np.array(masked_image)
    img_array[:, :, 3] = img_array[:, :, 3] * mask_array

    masked_image = Image.fromarray(img_array)

    # Crop to bounding box
    x1, y1, x2, y2 = bbox
    cropped_image = masked_image.crop((x1, y1, x2, y2))

    # Convert back to RGB if needed (remove alpha if fully opaque)
    if cropped_image.mode == "RGBA":
        # Check if we can convert to RGB (all pixels are opaque)
        alpha = np.array(cropped_image.split()[3])
        if np.all(alpha == 255):
            cropped_image = cropped_image.convert("RGB")

    return cropped_image


def convert_mask_image_to_points(
    mask: Image.Image, num_points: int = 10
) -> List[Tuple[int, int]]:
    if mask.mode != "L":
        mask = mask.convert("L")
    mask_arr = np.array(mask)
    ys, xs = np.where(mask_arr > 127)
    if xs.size == 0:
        return []
    count = min(num_points, xs.size)
    if count <= 0:
        return []
    indices = np.linspace(0, xs.size - 1, count, dtype=int)
    return [(int(xs[i]), int(ys[i])) for i in indices]
