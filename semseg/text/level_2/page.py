from semseg.text.level_2.tools import *
from pdfminer.layout import *

import sys
sys.dont_write_bytecode = True

def PageExtraction(PageLayout):
    PageHeight = PageLayout.height
    Page = []

    for Box in PageLayout:
        if isinstance(Box, LTTextBoxHorizontal) and PageHeight > 5*Box.y1:
            for item in Box:
                itemText = item.get_text()[:-1].replace(' ', '')
                if itemText.isdigit():
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
