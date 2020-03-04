import re
import sys
from pdfminer.layout import *
from utils.logging.syslog import Logger

sys.dont_write_bytecode = True

def TabNotePostProcess(TabNoteList):
    TNoteType = TabNoteTypeCheck(TabNoteList)

    if not TNoteType == None:
        for pgNum in range(len(TabNoteList)):
            PageTabNote = TabNoteList[pgNum]
            for tabNoteIndex in range(len(PageTabNote) - 1, -1, -1):
                tabNote = PageTabNote[tabNoteIndex]
                tabNoteText = tabNote[1].get_text()[:-1].lower()
                Type = TypeCalculate(tabNoteText)
                if not Type == TNoteType:
                    PageTabNote.remove(tabNote)

        TNoteList = []
        for pgNum in range(len(TabNoteList)):
            TNoteList.append([])
            PageTabNote = TabNoteList[pgNum]
            for tabNoteIndex in range(len(PageTabNote)):
                tabNote = PageTabNote[tabNoteIndex]
                AggTabNote = NoteAggregation(tabNote[0], tabNote[1], tabNote[2])
                TNoteList[pgNum].append(AggTabNote)

        return TNoteList

    else:
        pgNum = len(TabNoteList)

        TabNoteList = []
        for index in range(pgNum):
            TabNoteList.append([])

        return TabNoteList


def TabNoteTypeCheck(TabNoteList):
    TypeList = []
    TypeCountList = []

    for pgNum in range(len(TabNoteList)):
        PageTabNote = TabNoteList[pgNum]
        for tabNoteIndex in range(len(PageTabNote)):
            tabNoteText = PageTabNote[tabNoteIndex][1].get_text()[:-1].lower()
            Type = TypeCalculate(tabNoteText)
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
            Logger.get_log(logging).critical('Same Type of TableNote　{}'.format(MaxTypeCount))
            logging.logger.handlers.clear()

            return MaxType

        else:
            return MaxTypeCount[0][0]
    else:
        logging = Logger(__name__)
        Logger.get_log(logging).critical('No TableNote')
        logging.logger.handlers.clear()
        return None

def TypeCalculate(tabNoteText):
    Type = ''
    NoSpaceText = tabNoteText.replace(" ", "")

    if NoSpaceText[5].isdigit():
        # greek numeral
        Type += '0'
        numEndIndex = 5
        if len(NoSpaceText) > 6:
            for numEndIndex in range(numEndIndex+1, len(NoSpaceText)):
                if not NoSpaceText[numEndIndex].isdigit():
                    break
            if NoSpaceText[numEndIndex].isdigit() or NoSpaceText[numEndIndex].isalpha():
                # table12
                Type += '0'
            elif NoSpaceText[numEndIndex] == ':':
                Type += '2'
            elif NoSpaceText[numEndIndex] == '.':
                Type += '1'
            else:
                Type += 'E'
        else:
            Type += '0'
    else:
        # i  ii  iii  iv  v  vi  vii  viii  ix  x  xi
        firstSpace = tabNoteText.find(" ")
        lastSpace = tabNoteText.rfind(" ")

        if firstSpace < 0:
            Type += 'EE'
        elif firstSpace == lastSpace:
            GreekText = tabNoteText.split(" ")[1]
            if GreekText[-1] == ':' and not re.match(r'(l?x{0,3}|x[lc])(v?i{0,3}|i[vx])$', GreekText[:-1]) == None:
                Type += '12'
            elif GreekText[-1] == '.' and not re.match(r'(l?x{0,3}|x[lc])(v?i{0,3}|i[vx])$', GreekText[:-1]) == None:
                Type += '11'
            elif not re.match(r'(l?x{0,3}|x[lc])(v?i{0,3}|i[vx])$', GreekText) == None:
                Type += '10'
            else:
                Type += 'EE'
        else:
            GreekText = tabNoteText.split(" ")[1].split(" ")[0]
            if GreekText[-1] == ':' and not re.match(r'(l?x{0,3}|x[lc])(v?i{0,3}|i[vx])$', GreekText[:-1]) == None:
                Type += '12'
            elif GreekText[-1] == '.' and not re.match(r'(l?x{0,3}|x[lc])(v?i{0,3}|i[vx])$', GreekText[:-1]) == None:
                Type += '11'
            elif not re.match(r'(l?x{0,3}|x[lc])(v?i{0,3}|i[vx])$', GreekText) == None:
                Type += '10'
            else:
                Type += 'EE'

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

def TableNoteExtraction(PageLayout):
    TableNote = []
    PageHeight = PageLayout.height

    for Box in PageLayout:
        if isinstance(Box, LTTextBoxHorizontal):
            for Line in Box:
                LineText = Line.get_text()[:-1].lower().replace(' ', '')
                tabPos = LineText.find('table')
                if tabPos == 0 and len(LineText) > 5:
                    TableNote.append([PageHeight, Line, Box])

    return TableNote