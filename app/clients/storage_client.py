import httpx

from app.env import STORAGE_API_URL


class StorageClient:
    def __init__(self, api_url: str):
        self._api_url = api_url
        self._client = httpx.AsyncClient(timeout=60.0)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client.aclose()

    async def close(self):
        await self._client.aclose()

    async def upload_file(self, file_bytes: bytes, filename: str) -> str:
        """Upload a file and return the file ID."""
        url = f"{self._api_url}/files"

        files = {"file": (filename, file_bytes)}

        response = await self._client.post(url, files=files)
        response.raise_for_status()

        result = response.json()
        return result["file_id"]

    async def download_file(self, file_id: str) -> bytes:
        """Download a file by its ID and return the file bytes."""
        url = f"{self._api_url}/files/{file_id}"

        response = await self._client.get(url)
        response.raise_for_status()

        return response.content

    async def replace_file(self, file_id: str, file_bytes: bytes, filename: str) -> str:
        """Replace an existing file with new content and return the file ID."""
        url = f"{self._api_url}/files/{file_id}"

        files = {"file": (filename, file_bytes)}

        response = await self._client.put(url, files=files)
        response.raise_for_status()

        result = response.json()
        return result["file_id"]

    async def delete_file(self, file_id: str) -> str:
        """Delete a file by its ID and return the file ID."""
        url = f"{self._api_url}/files/{file_id}"

        response = await self._client.delete(url)
        response.raise_for_status()

        result = response.json()
        return result["file_id"]


storage_client = StorageClient(STORAGE_API_URL)
