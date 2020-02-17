
from pdf2image import convert_from_path
import tempfile

def pdf2image(fileName):
    with tempfile.TemporaryDirectory() as path:
        PagesImage = convert_from_path(fileName, output_folder = path)
    return PagesImage