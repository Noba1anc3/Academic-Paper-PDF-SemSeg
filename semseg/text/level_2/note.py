from pdfminer.layout import *
from semseg.text.level_2.tools import BlockRange


def NoteExtraction(PageLayout):
    Note = [[],[]]
    NoteLine = []
    ntIndex = []

    Blocks = BlockRange(PageLayout)
    LBlock = Blocks[0]
    RBlock = Blocks[2]

    for layoutItem in PageLayout:
        if isinstance(layoutItem, LTLine):
            if layoutItem.y0 == layoutItem.y1 and layoutItem.y0 < 0.2 * PageLayout.height:
                linePageRatio = (layoutItem.x1 - layoutItem.x0) / PageLayout.x1
                if linePageRatio > 0.085 and linePageRatio < 0.115:
                    LineLX = layoutItem.x0
                    if abs(LineLX - LBlock) < 10 or abs(LineLX - RBlock) < 10:
                        NoteLine.append(layoutItem)
                elif linePageRatio > 0.14 and linePageRatio < 0.17:
                    LineLX = layoutItem.x0
                    if abs(LineLX - LBlock) < 10 or abs(LineLX - RBlock) < 10:
                        NoteLine.append(layoutItem)

    for Bindex in range(len(PageLayout)):
        Box = PageLayout._objs[Bindex]
        if isinstance(Box, LTTextBoxHorizontal):
            for Lindex in range(len(NoteLine)):
                Line = NoteLine[Lindex]
                if Line.x0 < PageLayout.width / 4 and Box.x0 < PageLayout.width / 4:
                    if Box.y1 <= Line.y0 + 10:
                        for line in Box:
                            Note[0].append(line)
                            ntIndex.append([Bindex, Lindex])

                if Line.x0 > PageLayout.width / 2 and Box.x0 > PageLayout.width / 2:
                    if Box.y1 <= Line.y0 + 10:
                        for line in Box:
                            Note[1].append(line)
                            ntIndex.append([Bindex, Lindex])

    if Note[0] == [] and Note[1] == []:
        return [], ntIndex
    elif (not Note[0] == []) and Note[1] == []:
        return [Note[0]], ntIndex
    elif (not Note[1] == []) and Note[0] == []:
        return [Note[1]], ntIndex
    else:
        return Note, ntIndex
