import sys
from pdfminer.layout import *

sys.dont_write_bytecode = True

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

def TableNoteExtraction(PageLayout, FileTNoteType):
    LineList = []
    TableNote = []
    PageHeight = PageLayout.height

    for Box in PageLayout:
        if isinstance(Box, LTLine):
            LineList.append(Box)

    for Box in PageLayout:
        if isinstance(Box, LTTextBoxHorizontal):
            for Line in Box:
                LineText = Line.get_text()[:-1].lower().replace(' ', '')
                tabPos = LineText.find('table')
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


    return TableNote, FileTNoteType