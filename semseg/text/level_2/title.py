import sys
from pdfminer.layout import *
from utils.logging.syslog import Logger

sys.dont_write_bytecode = True

def TitleExtraction(PageLayout):
    title = []
    titleHeight = -1
    titleIndex = -1
    Height = PageLayout.height

    for index in range(len(PageLayout._objs)):
        item = PageLayout._objs[index]
        if item.y0 > 0.8 * Height:
            if isinstance(item, LTTextBoxHorizontal):
                for line in item:
                    if isinstance(line, LTTextLineHorizontal):
                        height = line.height
                        if height > 1.3 * titleHeight:
                            titleHeight = height
                            titleIndex = index
                            title = item
                            break
                        else:
                            break
    if title == []:
        logging = Logger(__name__)
        Logger.get_log(logging).critical('No Title Found')
        logging.logger.handlers.clear()

    return title, titleIndex