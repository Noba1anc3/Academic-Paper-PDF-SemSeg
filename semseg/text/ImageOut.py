
def ImageOut(PgHeight, Text, Image):
    # 剔除文字部分的正文部分当中在图片内部的文字

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

    return Text

def BoxInsideCheck(Box1, Box2):
    # 检查Box2是否在Box1当中
    if Box1[0] <= Box2[0] and Box1[2] >= Box2[2] and Box1[1] <= Box2[1] and Box1[3] >= Box2[3]:
        return True
    else:
        return False