import sys
from pdfminer.layout import *

sys.dont_write_bytecode = True

class HALF:
    pass

class FULL:
    pass

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

def overlap(lineA, lineB):
    lengthA = lineA[1] - lineA[0]
    lengthB = lineB[1] - lineB[0]

    if lineA[1] <= lineB[0]:
        return 0
    if lineA[0] >= lineB[1]:
        return 0
    if lineA[0] <= lineB[0] and lineB[1] <= lineA[1]:
        return 1
    if lineB[0] <= lineA[0] and lineA[1] <= lineB[1]:
        return 1

    lap = lineA[1] - lineB[0]
    if lap < min(lengthA, lengthB):
        return lap/min(lengthA, lengthB)
    else:
        lap = lineB[1] - lineA[0]
        return lap/min(lengthA, lengthB)

def BlockRange(PageLayout):
    PageWidth = PageLayout.width
    HF = half_full_judge(PageLayout)

    longestLHeight = -1
    longestRHeight = -1
    longestLBox = None
    longestRBox = None

    LBOX_LeftX = -1
    RBOX_LeftX = -1
    LBOX_RightX = -1
    RBOX_RightX = -1

    for Box in PageLayout:
        if HF == HALF:
            if Box.width*3 > PageWidth and Box.width*2 < PageWidth:
                if Box.x0 < PageWidth/4:
                    BoxHeight = Box.height
                    if BoxHeight > longestLHeight:
                        longestLHeight = BoxHeight
                        longestLBox = Box
                if Box.x1 > 3*PageWidth/4:
                    BoxHeight = Box.height
                    if BoxHeight > longestRHeight:
                        longestRHeight = BoxHeight
                        longestRBox = Box
        else:
            if Box.width*2 > PageWidth:
                BoxHeight = Box.height
                if BoxHeight > longestLHeight:
                    longestLHeight = BoxHeight
                    longestLBox = Box
                    longestRBox = Box

    if not longestLBox == None:
        LBOX_LeftX = int(longestLBox.x0)
        LBOX_RightX = int(longestLBox.x1)

    if not longestRBox == None:
        RBOX_LeftX = int(longestRBox.x0)
        RBOX_RightX = int(longestRBox.x1)

    return [LBOX_LeftX, LBOX_RightX, RBOX_LeftX, RBOX_RightX]


