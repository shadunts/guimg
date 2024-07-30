from algorithms.preprocessing.Zero_DCE.lowlight_test import lowlight
from PIL import Image

def main(image_path):
    data_lowlight = Image.open(image_path)
    return lowlight(data_lowlight)