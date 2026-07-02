"""Application entrypoint exposing the waste classification API."""

import io

import uvicorn
from fastapi import File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from PIL import Image, UnidentifiedImageError

from configs import get_settings
from src.model import UnknownMaterialError
from src.viewer import Viewer

servapp = Viewer()


@servapp.post("/greener/upload/dechets")
async def upload_file(file: UploadFile = File(...)) -> JSONResponse:
    """Classify an uploaded waste image and return its bin color.

    Args:
        file: The uploaded image file.

    Returns:
        A JSON response with the material name and bin color.

    Raises:
        HTTPException: If the file is not a valid image (400) or if the
            material cannot be classified into a known bin (422).

    """
    content = await file.read()
    try:
        image = Image.open(io.BytesIO(content))
        image.load()
    except UnidentifiedImageError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is not a valid image.",
        ) from exc

    try:
        response = await servapp.get_response(image)
    except UnknownMaterialError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return JSONResponse(response.model_dump())


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(app=servapp, host=settings.host, port=settings.port)
