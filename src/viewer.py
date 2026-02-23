from fastapi import FastAPI
from .controler import Controler
from .model import Response
from PIL import Image


class Viewer(FastAPI):
    controler: Controler

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controler = Controler()

    def get_response(self, image: Image.Image) -> Response:
        return self.controler.get_model_response(image)
