from PIL import Image
from .model import Model, Response


class Controler:
    model: Model

    def __init__(self) -> None:
        self.model = Model()

    def get_model_response(self, image: Image.Image) -> Response:
        return self.model.predict_material(image)
