from pdfminer.layout import *
from semseg.text.level_2.tools import BlockRange


def NoteExtraction(PageLayout):
    Note = [[],[]]
    NoteLine = []

    Blocks = BlockRange(PageLayout)
    LBlock = Blocks[0]
    RBlock = Blocks[2]

    for layoutItem in PageLayout:
        if isinstance(layoutItem, LTLine):
            if layoutItem.y0 == layoutItem.y1 and layoutItem.y0 < 0.2 * PageLayout.height:
                linePageRatio = (layoutItem.x1 - layoutItem.x0) / PageLayout.x1
                if linePageRatio > 0.085 and linePageRatio < 0.115:
                    LineLX = layoutItem.x0
                    if abs(LineLX - LBlock) < 5 or abs(LineLX - RBlock) < 5:
                        NoteLine.append(layoutItem)
                elif linePageRatio > 0.14 and linePageRatio < 0.17:
                    LineLX = layoutItem.x0
                    if abs(LineLX - LBlock) < 5 or abs(LineLX - RBlock) < 5:
                        NoteLine.append(layoutItem)

    for Box in PageLayout:
        if isinstance(Box, LTTextBoxHorizontal):
            for Line in NoteLine:
                if Line.x0 < PageLayout.width / 4 and Box.x0 < PageLayout.width / 4:
                    if Box.y1 < Line.y0:
                        for line in Box:
                            Note[0].append(line)

                if Line.x0 > PageLayout.width / 2 and Box.x0 > PageLayout.width / 2:
                    if Box.y1 < Line.y0:
                        for line in Box:
                            Note[1].append(line)

    if Note[0] == [] and Note[1] == []:
        return []
    elif (not Note[0] == []) and Note[1] == []:
        return [Note[0]]
    elif (not Note[1] == []) and Note[0] == []:
        return [Note[1]]
    else:
        return Note
