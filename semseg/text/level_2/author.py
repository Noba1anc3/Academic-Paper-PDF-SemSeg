import sys
from pdfminer.layout import *
from utils.logging.syslog import Logger

sys.dont_write_bytecode = True

def AuthorExtraction(PageLayout, TitleIndex):
    author = []
    breakSign = False

    for index in range(TitleIndex + 1, len(PageLayout._objs)):
        Box = PageLayout._objs[index]
        if isinstance(Box, LTTextBoxHorizontal):
            for line in Box:
                lineText = line.get_text()[:-1].replace(' ', '').lower()
                if lineText.find('abstract') >= 0:
                    abstractIndex = index
                    abstractUpY = line.y1
                    breakSign = True
                    break
            if breakSign:
                break

    if not breakSign:
        logging = Logger(__name__)
        Logger.get_log(logging).critical('No Abstract Found')
        logging.logger.handlers.clear()

        for index in range(TitleIndex, len(PageLayout._objs)):
            Box = PageLayout._objs[index]
            if isinstance(Box, LTTextBoxHorizontal):
                for line in Box:
                    lineText = line.get_text()[:-1].replace(' ', '').lower()
                    if lineText.find('introduction') >= 0:
                        abstractIndex = index
                        abstractUpY = line.y1
                        breakSign = True
                        break
                if breakSign:
                    break

    if not breakSign:
        logging = Logger(__name__)
        Logger.get_log(logging).critical('No Introduction Found')
        logging.logger.handlers.clear()

    Width = PageLayout.width
    Height = PageLayout.height

    if not breakSign:
        author.append(PageLayout._objs[TitleIndex + 1])
    else:
        for index in range(TitleIndex+1, abstractIndex):
            Box = PageLayout._objs[index]
            if Box.y0 > abstractUpY and Box.y0 > 0.6 * Height and isinstance(Box, LTTextBoxHorizontal):
                if (Box.x0 + Box.x1) > Width/4 and (Box.x0 + Box.x1) < 7*Width/4:
                    author.append(Box)

    return author
