"""Waste classification model wrapper with asynchronous inference support."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import ClassVar

import pydantic
import transformers
from PIL import Image

from configs import get_settings

FR_BIN_COLOR_CODE: dict[str, str] = {
    "cardboard": "Poubelle JAUNE (emballages)",
    "glass": "Poubelle VERTE (verre)",
    "metal": "Poubelle JAUNE (emballages)",
    "paper": "Poubelle BLEUE (papier)",
    "plastic": "Poubelle JAUNE (plastique)",
    "trash": "Poubelle NOIRE (ordures)",
    "organic": "Poubelle MARRON (biodechets)",
}


class UnknownMaterialError(Exception):
    """Raised when a predicted material has no known bin color mapping."""

    def __init__(self, material_name: str) -> None:
        """Initialize the error with the offending material name.

        Args:
            material_name: The material label returned by the model that
                could not be mapped to a bin color.

        """
        self.material_name = material_name
        super().__init__(f"Unknown material: {material_name}")


class Response(pydantic.BaseModel):
    """Structured prediction response returned by the model.

    Attributes:
        material_name: The lowercase label of the detected material.
        bin_color: The French bin color instruction for the material.

    """

    material_name: str
    bin_color: str

    @classmethod
    def from_material(cls, material_name: str) -> "Response":
        """Build a response from a raw material name.

        Args:
            material_name: The material label produced by the classifier.

        Returns:
            A fully populated Response instance.

        Raises:
            UnknownMaterialError: If the material has no bin mapping.

        """
        if material_name not in FR_BIN_COLOR_CODE:
            raise UnknownMaterialError(material_name)
        return cls(
            material_name=material_name,
            bin_color=FR_BIN_COLOR_CODE[material_name],
        )


class Model:
    """Asynchronous wrapper around a Hugging Face
    image-classification pipeline.

    The blocking inference call is offloaded to a thread pool so that the
    FastAPI event loop remains responsive under concurrent requests.
    """

    _executor: ClassVar[ThreadPoolExecutor] = ThreadPoolExecutor()
    model: transformers.Pipeline

    def __init__(self) -> None:
        """Initialize the classification pipeline from settings."""
        settings = get_settings()
        self.model = transformers.pipeline(
            "image-classification",
            model=settings.pipeline_model_name,
        )

    def _run_inference(self, image: Image.Image) -> str:
        """Run the synchronous pipeline and extract the top label.

        Args:
            image: The PIL image to classify.

        Returns:
            The lowercase label with the highest score.

        """
        result = self.model(image)
        return result[0]["label"].lower()

    async def predict_material(self, image: Image.Image) -> Response:
        """Asynchronously classify an image and map it to a bin color.

        Args:
            image: The PIL image to classify.

        Returns:
            A Response holding the material name and its bin color.

        Raises:
            UnknownMaterialError: If the predicted material is unmapped.

        """
        loop = asyncio.get_running_loop()
        material_name = await loop.run_in_executor(
            self._executor,
            self._run_inference,
            image,
        )
        return Response.from_material(material_name)
