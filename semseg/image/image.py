from pdfminer.layout import *

import sys
sys.dont_write_bytecode = True

def ImgExtraction(PageLayout):
    Figure = []
    for Box in PageLayout:
        if isinstance(Box, LTFigure):
            #和论文一样宽
            #和文字部分有交叉
            #和文字部分重合
            #空白部分能否去除
            #最顶上一群奇奇怪怪的框 automatic

            Figure.append(Box)

    return Figure