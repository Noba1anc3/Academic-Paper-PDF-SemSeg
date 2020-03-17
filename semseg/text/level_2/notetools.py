from semseg.text.level_2.image_note import *
from semseg.text.level_2.table_note import *

def NotePostProcess(NoteList, ForT):
    if ForT == 'F':
        NoteType = FNTypeCheck(NoteList)
    else:
        NoteType = TNTypeCheck(NoteList)

    if not NoteType == None:
        for pgNum in range(len(NoteList)):
            PageNote = NoteList[pgNum]
            for NoteIndex in range(len(PageNote) - 1, -1, -1):
                Note = PageNote[NoteIndex]
                NoteText = Note[1].get_text()[:-1].lower()
                if ForT == 'F':
                    Type = FNTypeCalculate(NoteText)
                else:
                    Type = TNTypeCalculate(NoteText)

                if not Type == NoteType:
                    PageNote.remove(Note)

        AggNoteList = []
        for pgNum in range(len(NoteList)):
            AggNoteList.append([])
            PageNote = NoteList[pgNum]
            for NoteIndex in range(len(PageNote)):
                Note = PageNote[NoteIndex]
                AggNote = NoteAggregation(Note[0], Note[1], Note[2])
                AggNoteList[pgNum].append(AggNote)
        return AggNoteList

    else:
        pgNum = len(NoteList)
        NoteList = []
        for index in range(pgNum):
            NoteList.append([])
        return NoteList

def NoteAggregation(PageHeight, Line, Box):
    NoteLX = Line.x0    # 锁定左侧横坐标
    LineHeight = Line.height
    AggNote = [Line]

    # aggregation in the direction of Right and Down
    for BoxLine in Box:
        if isinstance(BoxLine, LTTextLineHorizontal):
            NoteRX = Line.x1
            NoteMX = (NoteLX + NoteRX)/2
            NoteUY = PageHeight - Line.y1
            NoteDY = PageHeight - Line.y0

            LineLX = BoxLine.x0
            LineMX = (LineLX + BoxLine.x1)/2
            LineUY = PageHeight - BoxLine.y1
            LineDY = PageHeight - BoxLine.y0

            if abs(LineLX - NoteRX) < 2*LineHeight:
                if 3*abs(LineUY - NoteUY) < LineHeight and 3*abs(LineDY - NoteDY) < LineHeight:
                    Line = BoxLine
                    AggNote.append(BoxLine)

            if 3*abs(LineLX - NoteLX) < LineHeight:     # 左对齐
                if LineUY - NoteDY > 0 and LineUY - NoteDY < 0.35*LineHeight:
                    Line = BoxLine
                    AggNote.append(BoxLine)
                if LineUY - NoteDY < 0 and NoteDY - LineUY < LineHeight:  # pdfminer识别错位
                    Line = BoxLine
                    AggNote.append(BoxLine)

            if 3*abs(LineMX - NoteMX) < LineHeight:     # 居中对齐
                if 4*abs(LineUY - NoteDY) < LineHeight:
                    Line = BoxLine
                    AggNote.append(BoxLine)

    return AggNote