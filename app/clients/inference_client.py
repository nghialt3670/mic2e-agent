import json
import logging
from io import BytesIO
from typing import List
from zipfile import ZipFile

import httpx
from PIL import Image

from app.env import INFERENCE_API_URL
from app.schemas.common_schemas import Box, GeneratedMask, MaskLabeledPoint

logger = logging.getLogger(__name__)


class InferenceClient:
    def __init__(self, api_url: str):
        self._api_url = api_url
        self._client = httpx.AsyncClient(
            timeout=300.0
        )  # Long timeout for inference operations

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client.aclose()

    async def close(self):
        await self._client.aclose()

    async def sam3_generate_mask(
        self,
        image: Image.Image,
        points: List[MaskLabeledPoint] = None,
        box: Box = None,
    ) -> Image.Image:
        """Generate a mask from an image using point prompts, box prompt, or both."""
        url = f"{self._api_url}/sam3/generate-mask"

        if points is None and box is None:
            raise ValueError("Either points or box must be provided")

        image_bytes = BytesIO()
        image.save(image_bytes, format="PNG")
        image_bytes.seek(0)

        files = {"image": ("image.png", image_bytes, "image/png")}
        data = {}

        if points is not None:
            data["points"] = json.dumps([p.model_dump() for p in points])
        if box is not None:
            data["box"] = json.dumps(box.model_dump())

        response = await self._client.post(url, files=files, data=data)
        response.raise_for_status()

        mask_bytes = BytesIO(response.content)
        return Image.open(mask_bytes).convert("L")

    async def sam3_generate_masks_by_text(
        self, image: Image.Image, text: str
    ) -> List[GeneratedMask]:
        """Generate multiple masks from an image using text prompt."""
        url = f"{self._api_url}/sam3/generate-masks"

        # Convert image to bytes
        image_bytes = BytesIO()
        image.save(image_bytes, format="PNG")
        image_bytes.seek(0)

        # Prepare form data
        files = {"image": ("image.png", image_bytes, "image/png")}
        data = {"text": text}

        response = await self._client.post(url, files=files, data=data)
        response.raise_for_status()

        # Read zip file from response
        zip_bytes = BytesIO(response.content)
        masks = []
        with ZipFile(zip_bytes, "r") as zip_file:
            for filename in zip_file.namelist():
                # Extract score from filename (format: "score.png")
                try:
                    score = float(filename.replace(".png", ""))
                except ValueError:
                    score = 0.0

                # Read mask image
                mask_data = zip_file.read(filename)
                mask_image = Image.open(BytesIO(mask_data)).convert("L")
                masks.append(GeneratedMask(image=mask_image, score=score))

        return masks

    async def object_clear_inpaint(
        self, image: Image.Image, mask: Image.Image, prompt: str
    ) -> Image.Image:
        """Perform inpainting on an image using a mask and prompt."""
        url = f"{self._api_url}/object-clear/inpaint"

        # Convert images to bytes
        image_bytes = BytesIO()
        image.save(image_bytes, format="PNG")
        image_bytes.seek(0)

        mask_bytes = BytesIO()
        mask.save(mask_bytes, format="PNG")
        mask_bytes.seek(0)

        # Prepare form data
        files = {
            "image": ("image.png", image_bytes, "image/png"),
            "mask": ("mask.png", mask_bytes, "image/png"),
        }
        data = {"prompt": prompt}

        response = await self._client.post(url, files=files, data=data)
        response.raise_for_status()

        # Read inpainted image from response
        result_bytes = BytesIO(response.content)
        return Image.open(result_bytes).convert("RGB")

    async def flux_generate(self, prompt: str) -> Image.Image:
        """Generate an image from a text prompt using Flux."""
        url = f"{self._api_url}/flux/generate"

        # Prepare form data
        data = {"prompt": prompt}

        response = await self._client.post(url, data=data)
        response.raise_for_status()

        # Read generated image from response
        result_bytes = BytesIO(response.content)
        return Image.open(result_bytes).convert("RGB")

    async def gligen_inpaint(
        self,
        image: Image.Image,
        prompt: str,
        phrases: List[str],
        locations: List[List[float]],
        seed: int = 42,
    ) -> Image.Image:
        """
        Inpaint an image using GLIGEN with text-box grounding.

        Args:
            image: Input image to inpaint
            prompt: Text prompt for inpainting
            phrases: List of text phrases for the masked regions
            locations: List of bounding boxes in normalized coordinates (0-1)
                      Each location is [x1, y1, x2, y2]
            seed: Random seed for reproducibility (default: 42)

        Returns:
            Inpainted image
        """
        url = f"{self._api_url}/gligen/inpaint"

        # Convert image to bytes
        image_bytes = BytesIO()
        image.save(image_bytes, format="PNG")
        image_bytes.seek(0)

        # Prepare form data
        files = {"image": ("image.png", image_bytes, "image/png")}
        data = {
            "prompt": prompt,
            "phrases": json.dumps(phrases),
            "locations": json.dumps(locations),
            "seed": seed,
        }

        response = await self._client.post(url, files=files, data=data)
        response.raise_for_status()

        # Read inpainted image from response
        result_bytes = BytesIO(response.content)
        return Image.open(result_bytes).convert("RGB")

    async def sd_inpaint(
        self,
        image: Image.Image,
        mask: Image.Image,
        prompt: str,
        negative_prompt: str = "",
        num_inference_steps: int = 50,
        guidance_scale: float = 7.5,
        seed: int = 42,
    ) -> Image.Image:
        """
        Inpaint an image using Stable Diffusion with a binary mask.

        Args:
            image: Input image to inpaint
            mask: Binary mask (white = inpaint, black = keep)
            prompt: Description of what to generate in masked areas
            negative_prompt: Description of what to avoid (default: "")
            num_inference_steps: Number of denoising steps (default: 50)
            guidance_scale: How closely to follow the prompt (default: 7.5)
            seed: Random seed for reproducibility (default: 42)

        Returns:
            Inpainted image
        """
        url = f"{self._api_url}/sd-inpaint/inpaint"
        logger.info(f"Inpainting image with URL: {url}")

        # Convert images to bytes
        image_bytes = BytesIO()
        image.save(image_bytes, format="PNG")
        image_bytes.seek(0)

        mask_bytes = BytesIO()
        mask.save(mask_bytes, format="PNG")
        mask_bytes.seek(0)

        # Prepare form data
        files = {
            "image": ("image.png", image_bytes, "image/png"),
            "mask": ("mask.png", mask_bytes, "image/png"),
        }
        data = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
            "seed": seed,
        }

        response = await self._client.post(url, files=files, data=data)
        response.raise_for_status()

        # Read inpainted image from response
        result_bytes = BytesIO(response.content)
        return Image.open(result_bytes).convert("RGB")


inference_client = InferenceClient(INFERENCE_API_URL)
