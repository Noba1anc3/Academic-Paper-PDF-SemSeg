
from pdfminer.layout import *
from extraction.tools import overlap

def FigNoteTypeCheck(FileFNoteType, FigNoteType):
    if len(FileFNoteType) == 0:
        return True
    for index in range(0,3):
        if not FileFNoteType[index] == FigNoteType[index]:
            return False
    return True

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

def FigureNoteExtraction(PageLayout, FileFNoteType):
    FigureNote = []
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

    return Figure, FigureNote, FileFNoteType