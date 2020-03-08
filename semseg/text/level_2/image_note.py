from semseg.text.level_2.tools import *
from utils.logging.syslog import Logger
#　同样类型的假图注混迹在其中，一个在文字里，一个在图片下

sys.dont_write_bytecode = True

def FigNotePostProcess(FigNoteList):
    FNoteType = FigNoteTypeCheck(FigNoteList)

    if not FNoteType == None:
        for pgNum in range(len(FigNoteList)):
            PageFigNote = FigNoteList[pgNum]
            for figNoteIndex in range(len(PageFigNote) - 1, -1, -1):
                figNote = PageFigNote[figNoteIndex]
                figNoteText = figNote[0].get_text()[:-1].lower().replace(" ", "")
                Type = TypeCalculate(figNoteText)
                if not Type == FNoteType:
                    PageFigNote.remove(figNote)

        FNoteList = []
        for pgNum in range(len(FigNoteList)):
            FNoteList.append([])
            PageFigNote = FigNoteList[pgNum]
            for figNoteIndex in range(len(PageFigNote)):
                figNote = PageFigNote[figNoteIndex]
                AggFigNote = NoteAggregation(figNote[2], figNote[0], figNote[1])
                FNoteList[pgNum].append(AggFigNote)

        return FNoteList
    else:
        pgNum = len(FigNoteList)

        FigNoteList = []
        for index in range(pgNum):
            FigNoteList.append([])

        return FigNoteList

def FigNoteTypeCheck(FigNoteList):
    TypeList = []
    TypeCountList = []

    for pgNum in range(len(FigNoteList)):
        PageFigNote = FigNoteList[pgNum]
        for figNoteIndex in range(len(PageFigNote)):
            figNote = PageFigNote[figNoteIndex]
            figNoteText = figNote[0].get_text()[:-1].lower().replace(" ", "")
            Type = TypeCalculate(figNoteText)
            TypeList.append(Type)

    for index in range(len(TypeList) - 1, -1, -1):
        item = TypeList[index]
        if item.find('E') >= 0:
            TypeList.remove(item)

    if not TypeList == []:
        while True:
            Type = TypeList[0]
            TypeCount = TypeList.count(Type)
            TypeCountList.append([Type, TypeCount])
            for index in range(len(TypeList) - 1, -1, -1):
                item = TypeList[index]
                if item == Type:
                    TypeList.remove(item)
            if len(TypeList) == 0:
                break

        MaxTypeCount = [[None, -1]]
        for index in range(len(TypeCountList)):
            TCPair = TypeCountList[index]
            count = TCPair[1]
            if count > MaxTypeCount[0][1]:
                MaxTypeCount[0][0] = TCPair[0]
                MaxTypeCount[0][1] = count

        for index in range(len(TypeCountList)):
            TCPair = TypeCountList[index]
            type = TCPair[0]
            count = TCPair[1]
            if count == MaxTypeCount[0][1] and not type == MaxTypeCount[0][0]:
                MaxTypeCount.append([TCPair[0], count])

        if len(MaxTypeCount) > 1:
            MaxType = '000'
            for item in MaxTypeCount:
                if item[0] > MaxType:
                    MaxType = item[0]

            logging = Logger(__name__)
            Logger.get_log(logging).critical('Same Type of ImageNote:　{}'.format(MaxTypeCount))
            logging.logger.handlers.clear()

            return MaxType

        else:
            return MaxTypeCount[0][0]
    else:
        logging = Logger(__name__)
        Logger.get_log(logging).critical('No ImageNote')
        logging.logger.handlers.clear()
        return None

def TypeCalculate(figNoteText):
    # figure1: / figure1. / figure1
    # fig.1 / fig.1. / fig.1:
    # figure (1) / fig (0)
    # with . (1) / without . (0)
    # : (2) / . (1) / alpha (0)

    Type = ''
    digitIndex = None

    for char in figNoteText:
        if char.isdigit():
            digitIndex = figNoteText.find(char)
            break

    if not digitIndex == None:
        if digitIndex == 6 or digitIndex == 7:
            Type += '1'
        elif digitIndex == 3 or digitIndex == 4:
            Type += '0'
        else:
            # Error
            Type += 'E'

        if figNoteText[digitIndex - 1] == '.':
            Type += '1'
        elif figNoteText[digitIndex - 1] == 'g' or figNoteText[digitIndex - 1] == 'e':
            Type += '0'
        else:
            # Error
            Type += 'E'

        if len(figNoteText) > digitIndex + 1:
            if figNoteText[digitIndex + 1] == ':':
                Type += '2'
            elif figNoteText[digitIndex + 1] == '.':
                Type += '1'
            elif figNoteText[digitIndex + 1].isalpha():
                Type += '0'
            else:
                Type += 'E'
        else:
            Type += 'E'
    else:
        Type += 'EEE'

    return Type

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

def FigureNoteExtraction(PageLayout):
    FigureNote = []
    PageHeight = PageLayout.height

    # Figure = []
    # LRC = []  #Line / Rect / Curve
    #
    # for Box in PageLayout:
    #     if isinstance(Box, LTFigure):
    #         Figure.append(Box)
    #     elif isinstance(Box, LTLine):
    #         LRC.append(Box)
    #     elif isinstance(Box, LTRect) or isinstance(Box, LTCurve):
    #         LRC.append(Box)

    for Box in PageLayout:
        if isinstance(Box, LTTextBoxHorizontal):
            for Line in Box:
                LineText = Line.get_text()[:-1].lower().replace(' ', '')
                figPos = LineText.find('fig')
                if figPos == 0:
                    # fig.1 / fig 2
                    if len(LineText) > 3 and (LineText[3] == '.' or LineText[3].isdigit()):
                        #if FLRC_Check(Line, Figure, LRC, PageHeight):
                        FigureNote.append([Line, Box, PageHeight])
                    else:
                        # figure 1 / figure. 2
                        if len(LineText) > 6 and LineText[3:6] == 'ure' and (LineText[6].isdigit() or LineText[6] == '.'):
                            #if FLRC_Check(Line, Figure, LRC, PageHeight):
                            FigureNote.append([Line, Box, PageHeight])

    return FigureNote



# def FLRC_Check(figNote, Figure, LRC, PageHeight):
#     LineHeight = figNote.height
#     figNoteUpY = PageHeight - figNote.y1
#     figNotelrX = [figNote.x0, figNote.x1]
#
#     for fig in Figure:
#         figDownY = PageHeight - fig.y0
#         figlrX = [fig.x0, fig.x1]
#         diff = figNoteUpY - figDownY
#         if diff < 5 * LineHeight and diff > 0:
#             if overlap(figNotelrX, figlrX) > 0:
#                 return True
#
#     for lrc in LRC:
#         lrcDownY = PageHeight - lrc.y0
#         lrclrX = [lrc.x0, lrc.x1]
#         diff = figNoteUpY - lrcDownY
#         if diff < 5 * LineHeight and diff > 0:
#             if overlap(figNotelrX, lrclrX) > 0:
#                 return True
#
#     return False