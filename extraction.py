
from pdfminer.layout import *
from logzero import logger

from utils.layout import *
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

def half_full_judge(PageLayout):
    # To judge whether the main_text block's width approximates to the page's width
    # or it approximates to half of the page's width
    # 判断正文块的宽度接近整个页面的宽度或是接近整个页面宽度的一半

    PageWidth = PageLayout.width
    TextBlockWidth = []
    ModeList = []  #众数列表

    for item in PageLayout:
        if isinstance(item, LTTextBoxHorizontal):
            itemWidth = item.width
            if 3*itemWidth > PageWidth:
                TextBlockWidth.append(itemWidth)
    TextBlockWidth.sort()

    for index in range(len(TextBlockWidth) - 1):
        itemL = TextBlockWidth[index]
        itemR = TextBlockWidth[index+1]
        if itemR - itemL <= 5:
            continue
        else:
            ModeList.append(itemL)
            ModeList.append(index)
            if index + 2 == len(TextBlockWidth):
                ModeList.append(itemR)
                ModeList.append(index + 1)

    if not len(ModeList) == 0:
        for index in range(len(ModeList)-1, 0, -2):
            if index - 2 > 0:
                ModeList[index] = ModeList[index] - ModeList[index-2]
        ModeList[1] += 1

    Mode = -1
    ModeCount = 0

    for index in range(1, len(ModeList), 2):
        count = ModeList[index]
        if count > ModeCount:
            Mode = ModeList[index-1]
            ModeCount = count

    if 2*Mode < PageWidth:
        return HALF
    else:
        return FULL

def noteExtraction(PageLayout, PageType):
    widthCheck = True
    PageHeight = PageLayout.height
    PageWidth = PageLayout.width

    for item in PageLayout:
        if isinstance(item, LTTextBoxHorizontal):
            if PageHeight > 5*item.y1:
                itemText = item.get_text()

                allDigit = True
                for char in itemText:
                    if not char.isdigit():
                        allDigit = False
                        break
                if allDigit:
                    print("Page", itemText)

                else:
                    itemWidth = item.width
                    if PageType == HALF:
                        if 2*itemWidth >= PageWidth:
                            widthCheck = False
                    if widthCheck:
                        text0 = item.get_text()[0]
                        if text0.isdigit():
                            print(item.get_text())

