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

    for Bindex in range(len(PageLayout)):
        Box = PageLayout._objs[Bindex]
        if isinstance(Box, LTTextBoxHorizontal):
            pass

    return