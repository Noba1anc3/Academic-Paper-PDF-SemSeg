
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

def FigNoteTypeCheck(FileFNoteType, FigNoteType):
    if len(FileFNoteType) == 0:
        return True
    for index in range(0,3):
        if not FileFNoteType[index] == FigNoteType[index]:
            return False
    return True

def TableNoteTypeCheck(FileTNoteType, TableNoteType):
    if len(FileTNoteType) == 0:
        return True
    for index in range(0,2):
        if not FileTNoteType[index] == TableNoteType[index]:
            return False
    return True

def LineCheck(TableNote, Line, PageHeight):
    LineHeight = TableNote[0].height
    NoteYTop = PageHeight
    NoteYDown = 0

    for NoteLine in TableNote:
        YTop = PageHeight - NoteLine.y1
        YDown = PageHeight - NoteLine.y0
        if YTop < NoteYTop:
            NoteYTop = YTop
        if YDown > NoteYDown:
            NoteYDown = YDown

    for line in Line:
        if line.y0 == line.y1:
            lineY = PageHeight - line.y1
            if NoteYTop - lineY > 0 and NoteYTop - lineY < 12*LineHeight:
                return True
            if lineY - NoteYDown > 0 and lineY - NoteYDown < 12*LineHeight:
                return True
    return False

def FLRC_Check(figNote, Figure, LRC, PageHeight):
    LineHeight = figNote.height
    figNoteUpY = PageHeight - figNote.y1
    figNotelrX = [figNote.x0, figNote.x1]

    for fig in Figure:
        figDownY = PageHeight - fig.y0
        figlrX = [fig.x0, fig.x1]
        diff = figNoteUpY - figDownY
        if diff < 5 * LineHeight and diff > 0:
            if overlap(figNotelrX, figlrX) > 0:
                return True

    for lrc in LRC:
        lrcDownY = PageHeight - lrc.y0
        lrclrX = [lrc.x0, lrc.x1]
        diff = figNoteUpY - lrcDownY
        if diff < 5 * LineHeight and diff > 0:
            if overlap(figNotelrX, lrclrX) > 0:
                return True

    return False

def NoteAggregation(PageHeight, Line, Box):
    fNoteLX = Line.x0
    fNoteRX = Line.x1
    fNoteUY = PageHeight - Line.y1
    fNoteDY = PageHeight - Line.y0
    LineHeight = Line.height
    AggFigNote = [Line]
    # aggregation in the direction of Right and Down
    for Line in Box:
        if isinstance(Line, LTTextLineHorizontal):
            LineLX = Line.x0
            LineUY = PageHeight - Line.y1
            LineDY = PageHeight - Line.y0
            if LineLX - fNoteRX > 0 and LineLX - fNoteRX < 2*LineHeight:
                if LineUY - fNoteUY > -1*LineHeight and LineUY - fNoteUY < LineHeight:
                    if LineDY - fNoteDY > -1*LineHeight and LineDY - fNoteDY < LineHeight:
                        fNoteRX = Line.x1
                        AggFigNote.append(Line)
            if LineLX - fNoteLX > -0.5*LineHeight and LineLX - fNoteLX < 0.5*LineHeight:
                if LineUY - fNoteUY > 0 and LineUY - fNoteUY < 1.5*LineHeight:
                    fNoteUY = LineUY
                    AggFigNote.append(Line)

    return AggFigNote

def figTableExtraction(PageLayout, FileFNoteType, FileTNoteType):
    FigureNote = []
    TableNote = []
    Figure = []
    LRC = []  #Line / Rect / Curve
    LineList = []

    PageHeight = PageLayout.height

    for Box in PageLayout:
        if isinstance(Box, LTFigure):
            Figure.append(Box)
        elif isinstance(Box, LTLine):
            LineList.append(Box)
            LRC.append(Box)
        elif isinstance(Box, LTRect) or isinstance(Box, LTCurve):
            LRC.append(Box)

    for Box in PageLayout:
        if isinstance(Box, LTTextBoxHorizontal):
            for Line in Box:
                LineText = Line.get_text()[:-1].lower().replace(' ', '')
                figPos = LineText.find('fig')
                tabPos = LineText.find('table')
                if figPos == 0:
                    FNoteType = []
                    # FNoteType[321]
                    # 3: figure(1) / fig(0)
                    # 2: with .(1) / without .(0)
                    # 1: :(2) / .(1) / alpha(0)
                    # fig. 1 / fig. 1. / fig. 1:
                    if len(LineText) > 6:
                        if LineText[3] == '.' and LineText[4].isdigit():
                            FNoteType.append(0)
                            FNoteType.append(1)
                            colon = LineText[5:7].find(':')
                            point = LineText[5:7].find('.')

                            if colon >= 0 and point < 0:
                                FNoteType.append(2)
                            elif colon < 0 and point >= 0:
                                FNoteType.append(1)
                            elif colon >= 0 and point >= 0:
                                if colon < point:
                                    FNoteType.append(2)
                                else:
                                    FNoteType.append(1)
                            else:
                                FNoteType.append(0)

                            if FLRC_Check(Line, Figure, LRC, PageHeight):
                                if FigNoteTypeCheck(FileFNoteType, FNoteType):
                                    AggFigNote = NoteAggregation(PageHeight, Line, Box)
                                    FigureNote.append(AggFigNote)
                                    FileFNoteType = FNoteType.copy()
                        else:
                            # figure 1: / figure 5.
                            if len(LineText) > 8 and LineText[3:6] == 'ure':
                                if LineText[6].isdigit():
                                    FNoteType.append(1)
                                    FNoteType.append(0)
                                    colon = LineText[7:9].find(':')
                                    point = LineText[7:9].find('.')

                                    if colon >= 0 and point < 0:
                                        FNoteType.append(2)
                                    elif colon < 0 and point >= 0:
                                        FNoteType.append(1)
                                    elif colon >= 0 and point >= 0:
                                        if colon < point:
                                            FNoteType.append(2)
                                        else:
                                            FNoteType.append(1)
                                    else:
                                        FNoteType.append(0)

                                    if FLRC_Check(Line, Figure, LRC, PageHeight):
                                        if FigNoteTypeCheck(FileFNoteType, FNoteType):
                                            AggFigNote = NoteAggregation(PageHeight, Line, Box)
                                            FigureNote.append(AggFigNote)
                                            FileFNoteType = FNoteType.copy()

                if tabPos == 0:
                    TNoteType = []
                    # TNoteType[21]
                    # 2: arabic numerals(1) / greek numerals(0)
                    # 1: :(2) / .(1) / alpha(0) / NULL(-1) for the situation:[Table I]
                    # table 1   (1 -1)
                    # table 1:  (1  2)
                    # table 4.  (1  1)
                    # table I   (0 -1)
                    # table II: (0  1)
                    if len(LineText) > 5:
                        digit = LineText[5]
                        if digit.isdigit():
                            TNoteType.append(1)
                        elif digit == 'i' or digit == 'v' or digit == 'x':
                            TNoteType.append(0)
                    if len(TNoteType) == 1:
                        if len(LineText) == 6:
                            TNoteType.append(-1)
                            AggTableNote = NoteAggregation(PageHeight, Line, Box)
                            if LineCheck(AggTableNote, LineList, PageHeight):
                                if TableNoteTypeCheck(FileTNoteType, TNoteType):
                                    TableNote.append(AggTableNote)
                                    FileTNoteType = TNoteType.copy()
                        else:
                            colon = LineText[6:].find(':')
                            point = LineText[6:].find('.')
                            if colon >= 0 and point < 0:
                                TNoteType.append(2)
                            elif point >= 0 and colon < 0:
                                TNoteType.append(1)
                            elif colon >= 0 and point >= 0:
                                if colon > point:
                                    TNoteType.append(1)
                                else:
                                    TNoteType.append(2)
                            else:
                                if TNoteType[0] == 0:
                                    if len(LineText) == 7:
                                        if LineText[5:7] == 'ii' or LineText[5:7] == 'iv'\
                                                or LineText[5:7] == 'vi' or LineText[5:7] == 'ix'\
                                                or LineText[5:7] == 'xi':
                                            TNoteType.append(-1)
                                        else:
                                            TNoteType.append(0)
                                    elif len(LineText) == 8:
                                        if LineText[5:8] == 'iii' or LineText[5:8] == 'vii'\
                                                or LineText[5:8] == 'xii':
                                            TNoteType.append(-1)
                                        else:
                                            TNoteType.append(0)
                                    elif len(LineText) == 9:
                                        if LineText[5:9] == 'viii':
                                            TNoteType.append(-1)
                                        else:
                                            TNoteType.append(0)
                                    else:
                                        TNoteType.append(0)
                                else:
                                    if len(LineText) == 7 and LineText[6].isdigit():
                                        TNoteType.append(-1)
                                    else:
                                        TNoteType.append(0)
                            AggTableNote = NoteAggregation(PageHeight, Line, Box)
                            if LineCheck(AggTableNote, LineList, PageHeight):
                                if TableNoteTypeCheck(FileTNoteType, TNoteType):
                                    TableNote.append(AggTableNote)
                                    FileTNoteType = TNoteType.copy()


    return Figure, FigureNote, TableNote, FileFNoteType, FileTNoteType


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
