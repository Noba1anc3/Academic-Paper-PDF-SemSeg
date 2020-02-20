
from pdfminer.layout import *

def TitleExtraction(PageLayout):
    title = None
    titleHeight = -1
    titleIndex = -1
    Height = PageLayout.height

    for index in range(len(PageLayout._objs)):
        item = PageLayout._objs[index]
        if item.y0 > 0.7 * Height:
            if isinstance(item, LTTextBoxHorizontal):
                for line in item:
                    if isinstance(line, LTTextLineHorizontal):
                        height = line.height
                        if height > titleHeight:
                            titleHeight = height
                            titleIndex = index
                            title = item
                            break
                        else:
                            break

    return [title], titleIndex