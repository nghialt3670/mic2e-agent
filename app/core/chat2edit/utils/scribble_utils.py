import re

from PIL import Image, ImageDraw

from app.core.chat2edit.models.scribble import Scribble


def convert_scribble_to_mask_image(scribble: Scribble, image: Image) -> Image.Image:
    image_pil = image.get_image()
    img_width, img_height = image_pil.size
    mask = Image.new("L", (img_width, img_height), 0)
    draw = ImageDraw.Draw(mask)

    path_data = scribble.path
    if not path_data:
        return mask
    if isinstance(path_data, str) and not path_data.strip():
        return mask
    if isinstance(path_data, list) and len(path_data) == 0:
        return mask

    scribble_left_img = scribble.left + img_width / 2
    scribble_top_img = scribble.top + img_height / 2
    origin_offset_x = scribble_left_img
    origin_offset_y = scribble_top_img

    current_x = 0
    current_y = 0
    points = []

    if isinstance(path_data, str):
        pattern = r"([MLQZ])\s*([-\d.]+(?:\s*[, ]\s*[-\d.]+)*)?"
        matches = re.findall(pattern, path_data.upper())

        for cmd_type, coords_str in matches:
            if cmd_type == "M":
                coords = (
                    [float(x.strip()) for x in re.split(r"[, ]+", coords_str.strip())]
                    if coords_str.strip()
                    else []
                )
                if len(coords) >= 2:
                    current_x = coords[0] + origin_offset_x
                    current_y = coords[1] + origin_offset_y
                    points = [(current_x, current_y)]
            elif cmd_type == "L":
                coords = (
                    [float(x.strip()) for x in re.split(r"[, ]+", coords_str.strip())]
                    if coords_str.strip()
                    else []
                )
                if len(coords) >= 2:
                    x = coords[0] + origin_offset_x
                    y = coords[1] + origin_offset_y
                    points.append((x, y))
                    current_x, current_y = x, y
            elif cmd_type == "Q":
                coords = (
                    [float(x.strip()) for x in re.split(r"[, ]+", coords_str.strip())]
                    if coords_str.strip()
                    else []
                )
                if len(coords) >= 4:
                    cp_x = coords[0] + origin_offset_x
                    cp_y = coords[1] + origin_offset_y
                    end_x = coords[2] + origin_offset_x
                    end_y = coords[3] + origin_offset_y
                    num_segments = 20
                    for i in range(num_segments + 1):
                        t = i / num_segments
                        x = (
                            (1 - t) ** 2 * current_x
                            + 2 * (1 - t) * t * cp_x
                            + t**2 * end_x
                        )
                        y = (
                            (1 - t) ** 2 * current_y
                            + 2 * (1 - t) * t * cp_y
                            + t**2 * end_y
                        )
                        points.append((x, y))
                    current_x, current_y = end_x, end_y
            elif cmd_type == "Z":
                if len(points) > 1:
                    points.append(points[0])
    else:
        path_commands = path_data
        for command in path_commands:
            if not command or len(command) < 2:
                continue
            cmd_type = str(command[0]).upper()

            if cmd_type == "M":
                if len(command) >= 3:
                    current_x = float(command[1]) + origin_offset_x
                    current_y = float(command[2]) + origin_offset_y
                    points = [(current_x, current_y)]
            elif cmd_type == "L":
                if len(command) >= 3:
                    x = float(command[1]) + origin_offset_x
                    y = float(command[2]) + origin_offset_y
                    points.append((x, y))
                    current_x, current_y = x, y
            elif cmd_type == "Q":
                if len(command) >= 5:
                    cp_x = float(command[1]) + origin_offset_x
                    cp_y = float(command[2]) + origin_offset_y
                    end_x = float(command[3]) + origin_offset_x
                    end_y = float(command[4]) + origin_offset_y
                    num_segments = 20
                    for i in range(num_segments + 1):
                        t = i / num_segments
                        x = (
                            (1 - t) ** 2 * current_x
                            + 2 * (1 - t) * t * cp_x
                            + t**2 * end_x
                        )
                        y = (
                            (1 - t) ** 2 * current_y
                            + 2 * (1 - t) * t * cp_y
                            + t**2 * end_y
                        )
                        points.append((x, y))
                    current_x, current_y = end_x, end_y
            elif cmd_type == "Z":
                if len(points) > 1:
                    points.append(points[0])

    if len(points) > 1:
        int_points = []
        for x, y in points:
            clamped_x = max(0, min(int(x), img_width - 1))
            clamped_y = max(0, min(int(y), img_height - 1))
            int_points.append((clamped_x, clamped_y))

        if len(int_points) < 2:
            return mask

        stroke_width = max(3, int(scribble.strokeWidth or 10))

        for i in range(len(int_points) - 1):
            draw.line([int_points[i], int_points[i + 1]], fill=255, width=stroke_width)

        point_radius = max(2, stroke_width // 2)
        for x, y in int_points:
            bbox = [
                x - point_radius,
                y - point_radius,
                x + point_radius,
                y + point_radius,
            ]
            draw.ellipse(bbox, fill=255)

        if len(int_points) > 2 and int_points[0] == int_points[-1]:
            draw.polygon(int_points, fill=255)

    return mask
