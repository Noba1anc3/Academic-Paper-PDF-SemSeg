from semseg.text.tools import *
from pdfminer.layout import *

def NoteExtraction(PageLayout, PageType):
    widthCheck = True
    PageHeight = PageLayout.height
    PageWidth = PageLayout.width

    Page = []
    Note = []

    for Box in PageLayout:
        if isinstance(Box, LTTextBoxHorizontal) and PageHeight > 5*Box.y1:
            for item in Box:
                itemText = item.get_text()[:-1].replace(' ', '')
                if itemText.isdigit():
                    Page.append(Box)
                else:
                    itemWidth = item.width
                    if PageType == HALF:
                        if 2*itemWidth >= PageWidth:
                            widthCheck = False
                    if widthCheck:
                        if len(itemText) > 2 and itemText[0].isdigit() and not itemText[1] == '.' and itemText[2].isalpha():
                            Note.append(Box)
                            break

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

    return Page, Note
