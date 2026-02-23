import transformers
import pydantic
import os
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

PIPELINE_MODEL_NAME = os.getenv('PIPELINE_MODEL_NAME')
FR_BIN_COLOR_CODE = {"cardboard": "Poubelle JAUNE (emballages)",
                     "glass": "Poubelle VERTE (verre)",
                     "metal": "Poubelle JAUNE (emballages)",
                     "paper": "Poubelle BLEUE (papier)",
                     "plastic": "Poubelle JAUNE (plastique)",
                     "trash": " Poubelle NOIRE (ordures)",
                     "organic": "Poubelle MARRON (biodéchets)"}


class Response(pydantic.BaseModel):
    material_name: str
    bin_color: str

    def __init__(self, material_name: str, **kwargs) -> None:
        bin_color = ''
        if material_name in FR_BIN_COLOR_CODE.keys():
            bin_color = FR_BIN_COLOR_CODE[material_name]
        else:
            raise Exception(f"Unknown material: {self.material_name}")
        super().__init__(
            material_name=material_name,
            bin_color=bin_color,
            **kwargs)


class Model:
    model: transformers.Pipeline

    def __init__(self) -> None:
        self.model = transformers.pipeline(
            "image-classification",
            model=PIPELINE_MODEL_NAME)

    def predict_material(self, image: Image.Image) -> Response:
        result = self.model(image)
        return Response(result[0]['label'].lower())
