import io
import json

import requests


def download_file_to_bytes(url: str) -> bytes:
    response = requests.get(url)
    return response.content


def create_buffer_from_dict(data: dict) -> io.BytesIO:
    buffer = io.BytesIO()
    buffer.write(json.dumps(data).encode("utf-8"))
    buffer.seek(0)
    return buffer
