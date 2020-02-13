
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

def figTableExtraction(PageLayout):
    Figure = []
    Table = []
    for Box in PageLayout:
        if isinstance(Box, LTTextBoxHorizontal):
            for Line in Box:
                LineText = Line.get_text()[:-1].lower().replace(' ', '')
                figPos = LineText.find('fig')
                tabPos = LineText.find('table')
                if figPos == 0:
                    # fig. 1 / fig. 1. / fig. 1:
                    if len(LineText) > 4:
                        if LineText[3] == '.' and LineText[4].isdigit():
                            Figure.append(Line)
                        else:
                            # figure 1: / figure 5.
                            if len(LineText) > 6 and LineText[3:6] == 'ure':
                                if LineText[6].isdigit():
                                    Figure.append(Line)

                if tabPos == 0:
                    # table 1 / table 1: / table 4. / table I /table II:
                    if len(LineText) > 5:
                        digit = LineText[tabPos+5]
                        if digit.isdigit():
                            Table.append(Line)
                        elif digit == 'i' or digit == 'v' or digit == 'x':
                            Table.append(Line)

    return Figure, Table


def noteExtraction(PageLayout, PageType):
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
