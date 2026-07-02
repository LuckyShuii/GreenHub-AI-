"""FastAPI application exposing the waste classification endpoints."""

from fastapi import FastAPI
from PIL import Image

from .controler import Controler
from .model import Response


class Viewer(FastAPI):
    """FastAPI application holding a controller instance."""

    controler: Controler

    def __init__(self, **kwargs: object) -> None:
        """Initialize the FastAPI app and its controller.

        Args:
            **kwargs: Keyword arguments forwarded to FastAPI.

        """
        super().__init__(**kwargs)  # type: ignore
        self.controler = Controler()

    async def get_response(self, image: Image.Image) -> Response:
        """Return the model response for an uploaded image.

        Args:
            image: The PIL image to classify.

        Returns:
            The classification Response.

        """
        return await self.controler.get_model_response(image)
