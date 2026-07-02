"""Unit tests for the controller layer with a mocked model."""

from unittest.mock import AsyncMock

import pytest
from PIL import Image

from src.controler import Controler
from src.model import Response


@pytest.mark.asyncio
async def test_controler_delegates_to_model(
    monkeypatch: pytest.MonkeyPatch, sample_image: Image.Image
) -> None:
    """The controller forwards the image and returns the model response."""
    expected = Response(material_name="glass", bin_color="Poubelle VERTE")
    monkeypatch.setattr(
        "src.controler.Model.__init__", lambda self: None
    )
    controler = Controler()
    controler.model = AsyncMock()
    controler.model.predict_material.return_value = expected

    result = await controler.get_model_response(sample_image)

    controler.model.predict_material.assert_awaited_once_with(sample_image)
    assert result == expected
