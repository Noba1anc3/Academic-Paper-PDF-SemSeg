from pdfminer.layout import *

def Level2Extraction(PageLayout, pgIndex, ntIndex, ttIndex, auIndex):
    # pgIndex: [BoxIndex] / []
    # ntIndex: [[BoxIndex, LineIndex], ...] / []
    # ttIndex: BoxIndex / -1
    # auIndex: [BoxIndex, ...] / []

    Text = []
    BoxLineList = []

    if not pgIndex == []:
        pgBox = pgIndex[0]
        BoxLineList.append([pgBox,-1])
    if not ttIndex == -1:
        BoxLineList.append([ttIndex, -1])
    for item in ntIndex:
        BoxLineList.append(item)
    for item in auIndex:
        BoxLineList.append([item, -1])

    BoxLineList.sort()

    for index in range(len(BoxLineList)-1, -1, -1):
        BoxLine = BoxLineList[index]
        Box = BoxLine[0]
        Line = BoxLine[1]
        if Line == -1:
            LTBox = PageLayout._objs[Box]
            PageLayout._objs.remove(LTBox)
        else:
            LTBox = PageLayout._objs[Box]
            LTLine = LTBox._objs[Line]
            LTBox._objs.remove(LTLine)
            if LTBox._objs == []:
                PageLayout._objs.remove(LTBox)

    for index in range(len(PageLayout._objs)-1, -1, -1):
        Box = PageLayout._objs[index]
        if not isinstance(Box, LTTextBoxHorizontal):
            PageLayout._objs.remove(Box)

    return PageLayout._objs

def FigTabNoteOut(Text, TabNote, FigNote):
    for index in range(len(Text)):
        PgText = Text[index]
        PgTNote = TabNote[index]
        PgFNote = FigNote[index]

        FTNote = []
        for TNote in PgTNote:
            for TNoteLine in TNote:
                FTNote.append(TNoteLine.get_text())
        for FNote in PgFNote:
            for FNoteLine in FNote:
                FTNote.append(FNoteLine.get_text())

        for Bindex in range(len(PgText) - 1, -1, -1):
            Box = PgText[Bindex]
            for Lindex in range(len(Box._objs)-1, -1, -1):
                Line = Box._objs[Lindex]
                LineText = Line.get_text()
                if LineText in FTNote:
                    Box._objs.remove(Line)
                    FTNote.remove(LineText)
            if Box._objs == []:
                PgText.remove(Box)
            if FTNote == []:
                break

    return Text