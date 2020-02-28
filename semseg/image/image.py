from pdfminer.layout import *

def ImgExtraction(PageLayout):
    Figure = []
    for Box in PageLayout:
        if isinstance(Box, LTFigure):
            Figure.append(Box)

    return Figure