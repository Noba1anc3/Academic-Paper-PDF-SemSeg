from semseg.text.level_2.tools import *
from pdfminer.layout import *

import sys
sys.dont_write_bytecode = True

def PageExtraction(PageLayout):
    PageHeight = PageLayout.height
    PageWidth = PageLayout.width
    Page = []

    for Box in PageLayout:
        if isinstance(Box, LTTextBoxHorizontal) and PageHeight > 6*Box.y1:
            for index in range(len(Box._objs)):
                line = Box._objs[index]
                if not index == 0:
                    break
                else:
                    lineXmid = (line.x0 + line.x1) / 2
                    lineText = line.get_text()[:-1].replace(' ', '')
                    if lineText.isdigit() and 0.4 <= lineXmid/PageWidth and lineXmid/PageWidth <= 0.6:
                        Page.append(Box)

        elif isinstance(Box, LTFigure) and PageHeight > 6*Box.y1:
            pg = True
            BoXmid = (Box.x0 + Box.x1) / 2
            for item in Box:
                if not (isinstance(item, LTChar) and item._text.isdigit()):
                    pg = False
                    break
            if pg and 0.4 <= BoXmid/PageWidth and BoXmid/PageWidth <= 0.6:
                Page.append(Box)

    if len(Page) > 1:
        smallestY = PageHeight
        smallestIndex = -1
        for index in range(len(Page)):
            LeftUpY = Page[index].y1
            if LeftUpY < smallestY:
                smallestY = LeftUpY
                smallestIndex = index

        realPage = Page[smallestIndex]
        Page = []
        Page.append(realPage)

    return Page
