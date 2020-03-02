from pdfminer.layout import *

import sys
sys.dont_write_bytecode = True

def ImgExtraction(PageLayout):
    Figure = []
    for Box in PageLayout:
        if isinstance(Box, LTFigure):
            Figure.append(Box)

    return Figure