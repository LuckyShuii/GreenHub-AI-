import uvicorn
from src.viewer import Viewer
from fastapi import UploadFile, File
from PIL import Image
import io
import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse

load_dotenv()
HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
servapp = Viewer()


@servapp.post("/greener/upload/dechets")
async def upload_file(file: UploadFile = File(...)) -> JSONResponse:
    content = await file.read()
    image = Image.open(io.BytesIO(content))
    return JSONResponse(servapp.get_response(image).model_dump())


if __name__ == "__main__":
    uvicorn.run(app=servapp, host=HOST, port=PORT)  # type: ignore
