from pdfminer.layout import *

import sys
sys.dont_write_bytecode = True

def ImgExtraction(PageLayout):
    Figure = []
    for Box in PageLayout:
        if isinstance(Box, LTFigure) and isinstance(Box._objs[0], LTImage):
            Figure.append(Box)

    return Figure