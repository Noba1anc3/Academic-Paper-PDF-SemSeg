
from pdfminer.layout import *
from logzero import logger

import numpy as np
import cv2
import os

def titleExtraction(PageLayout):
    error = True
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
                            error = False
                            break
                        else:
                            break
                    else:
                        logger.info("{} in TextBoxHorizontal".format(str(type(line))))

    return [title], titleIndex, error

def AuthorExtraction(PageLayout, titleIndex):
    author = []
    abstractIndex = titleIndex + 2
    breakSign = False

    for index in range(titleIndex+1, len(PageLayout._objs)):
        box = PageLayout._objs[index]
        if isinstance(box, LTTextBoxHorizontal):
            for line in box:
                line = line.get_text()[:-1].replace(' ', '').lower()
                if line.find('abstract') >= 0:
                    abstractIndex = index
                    breakSign = True
                    break
            if breakSign:
                break

    Width = PageLayout.width
    Height = PageLayout.height
    for index in range(titleIndex+1, abstractIndex):
        item = PageLayout._objs[index]
        if item.y0 > 0.6 * Height and isinstance(item, LTTextBoxHorizontal):
            if (item.x0 + item.x1) > 2*Width/5 and (item.x0 + item.x1) < 8*Width/5:
                author.append(PageLayout._objs[index])

    return author
