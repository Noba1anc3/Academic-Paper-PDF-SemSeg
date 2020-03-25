from utils.logging.syslog import Logger
from semseg.text.level_2.tools import *

def FNTypeCheck(FigNoteList):
    TypeList = []
    TypeCountList = []

    for pgNum in range(len(FigNoteList)):
        PageFigNote = FigNoteList[pgNum]
        for figNoteIndex in range(len(PageFigNote)):
            figNote = PageFigNote[figNoteIndex]

            figNoteText = figNote[1].get_text()[:-1].lower().replace(" ", "")
            Type = FNTypeCalculate(figNoteText)
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

def FNTypeCalculate(figNoteText):
    # figure1: / figure1. / figure1
    # fig.1 / fig.1. / fig.1:
    # figure (1) / fig (0)
    # with . (1) / without . (0)
    # : (2) / . (1) / alpha (0)

    Type = ''
    digitIndex = None
    figNoteText = figNoteText.replace(" ", "")

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

def FigureNoteExtraction(PageLayout):
    FigureNote = []
    PageHeight = PageLayout.height

    for Box in PageLayout:
        if isinstance(Box, LTTextBoxHorizontal):
            for Line in Box:
                LineText = Line.get_text()[:-1].lower().replace(' ', '')
                figPos = LineText.find('fig')
                if figPos == 0:
                    # fig.1 / fig 2
                    if len(LineText) > 3 and (LineText[3] == '.' or LineText[3].isdigit()):
                        FigureNote.append([PageHeight, Line, Box])
                    else:
                        # figure 1 / figure. 2
                        if len(LineText) > 6 and LineText[3:6] == 'ure' and (LineText[6].isdigit() or LineText[6] == '.'):
                            FigureNote.append([PageHeight, Line, Box])

    return FigureNote