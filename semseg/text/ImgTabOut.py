
def ImgTabOut(PgHeight, Text, Image, Table):
    # 剔除文字部分的正文部分当中在图片和表格内部的文字
    for PageNo in range(len(Text)):
        PgText = Text[PageNo]
        PgImage = Image[PageNo]
        if not PgImage == [] and not PgText == []:
            for img in PgImage:
                imgLoc = [img.x0, PgHeight - img.y1, img.x1, PgHeight - img.y0]
                for index in range(len(PgText)-1, -1, -1):
                    Box = PgText[index]
                    BoxLoc = [Box.x0, PgHeight - Box.y1, Box.x1, PgHeight - Box.y0]
                    if BoxInsideCheck(imgLoc, BoxLoc):
                        PgText.remove(Box)
                    else:
                        for index in range(len(Box._objs)-1, -1, -1):
                            Line = Box._objs[index]
                            LineLoc = [Line.x0, PgHeight - Line.y1, Line.x1, PgHeight - Line.y0]
                            if BoxInsideCheck(imgLoc, LineLoc):
                                Box._objs.remove(Line)
                        if Box._objs == []:
                            PgText.remove(Box)

    for PageNo in range(len(Text)):
        PgText = Text[PageNo]
        PgTable = Table[PageNo]
        if not PgTable == [] and not PgText == []:
            for tab in PgTable:
                tabLoc = [tab.x0, PgHeight - tab.y1, tab.x1, PgHeight - tab.y0]
                for index in range(len(PgText)-1, -1, -1):
                    Box = PgText[index]
                    BoxLoc = [Box.x0, PgHeight - Box.y1, Box.x1, PgHeight - Box.y0]
                    if BoxInsideCheck(tabLoc, BoxLoc):
                        PgText.remove(Box)
                    else:
                        for index in range(len(Box._objs)-1, -1, -1):
                            Line = Box._objs[index]
                            LineLoc = [Line.x0, PgHeight - Line.y1, Line.x1, PgHeight - Line.y0]
                            if BoxInsideCheck(tabLoc, LineLoc):
                                Box._objs.remove(Line)
                        if Box._objs == []:
                            PgText.remove(Box)

    return Text

def TableOut(PgHeight, TableNotes, Tables):
    # 剔除文字部分的正文部分当中在图片和表格内部的文字
    for PageNo in range(len(TableNotes)):
        PgTableNote = TableNotes[PageNo]
        PgTable = Tables[PageNo]
        if not PgTable == [] and not PgTableNote == []:
            for tab in PgTable:
                tabLoc = [tab.x0, PgHeight - tab.y1, tab.x1, PgHeight - tab.y0]
                for index in range(len(PgTableNote)-1, -1, -1):
                    TableNote = PgTableNote[index]
                    for index in range(len(TableNote)-1, -1, -1):
                        Line = TableNote[index]
                        LineLoc = [Line.x0, PgHeight - Line.y1, Line.x1, PgHeight - Line.y0]
                        if BoxInsideCheck(tabLoc, LineLoc):
                            TableNote.remove(Line)
                    if TableNote == []:
                        TableNotes.remove(TableNote)

    return TableNotes

def BoxInsideCheck(Box1, Box2):
    # 检查Box2是否在Box1当中
    BoxXMid = (Box2[0] + Box2[2])/2
    BoxYMid = (Box2[1] + Box2[3])/2

    if Box1[0] <= BoxXMid and Box1[2] >= BoxXMid and Box1[1] <= BoxYMid and Box1[3] >= BoxYMid:
        return True
    else:
        return False