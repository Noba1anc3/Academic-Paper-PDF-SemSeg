
from pdfminer.layout import *

def coordinateChange(Image, Layout, item):
    ImageSize = Image.shape
    LayoutWidth = Layout.width
    LayoutHeight = Layout.height
    liRatio = [LayoutWidth / ImageSize[1], LayoutHeight / ImageSize[0]]

    XleftUp = int(item.x0 / liRatio[0])
    YleftUp = int((LayoutHeight - item.y1) / liRatio[1])
    XrightDown = int(item.x1 / liRatio[0])
    YrightDown = int((LayoutHeight - item.y0) / liRatio[1])

    location = [XleftUp, YleftUp, XrightDown, YrightDown]

    return location

def NoteBBoxes(Image, Layout, LTBBoxes):
    # 针对图注类型特殊处理的计算其BBoxes的方法，其中LTBBoxes的每一项为一个列表
    # 每一个列表都是一个图注，列表内部由若干个LTTextLineHorizontal组成

    BBoxes = []
    for index in range(len(LTBBoxes)):
        Block = LTBBoxes[index]
        SafeCheck = False
        BBoxes.append([])
        for Line in Block:
            location = coordinateChange(Image, Layout, Line)
            XleftUp = location[0]
            YleftUp = location[1]
            XrightDown = location[2]
            YrightDown = location[3]

            if SafeCheck:
                # 该目的为确定出所有LTTextBoxHorizontal所组成的大区域并置为该方法返回的BBoxes的第一项
                if XleftUp < BBoxes[index][0][0]:
                    BBoxes[index][0][0] = XleftUp
                if YleftUp < BBoxes[index][0][1]:
                    BBoxes[index][0][1] = YleftUp
                if XrightDown > BBoxes[index][0][2]:
                    BBoxes[index][0][2] = XrightDown
                if YrightDown > BBoxes[index][0][3]:
                    BBoxes[index][0][3] = YrightDown
            else:
                SafeCheck = True
                BBoxes[index].append(location)

            BBoxes[index].append(location.copy())

    return BBoxes

def getBBoxes(Image, Layout, LTBBoxes):
    # 根据Layout的高度和liRatio将从Layout提取出来的坐标转换为Image上的坐标
    # 传入进来的LTBBoxes或者由若干个LTTextBoxHorizontal组成，或者由若干个LTTextLineHorizontal组成

    BBoxes = []
    SafeCheck = False

    for BBox in LTBBoxes:
        location = coordinateChange(Image, Layout, BBox)
        XleftUp = location[0]
        YleftUp = location[1]
        XrightDown = location[2]
        YrightDown = location[3]

        if SafeCheck:
            # 该目的为确定出所有LTTextBoxHorizontal所组成的大区域并置为该方法返回的BBoxes的第一项
            if XleftUp < BBoxes[0][0]:
                BBoxes[0][0] = XleftUp
            if YleftUp < BBoxes[0][1]:
                BBoxes[0][1] = YleftUp
            if XrightDown > BBoxes[0][2]:
                BBoxes[0][2] = XrightDown
            if YrightDown > BBoxes[0][3]:
                BBoxes[0][3] = YrightDown
        else:
            SafeCheck = True
            BBoxes.append(location)

        if isinstance(BBox, LTTextBoxHorizontal):
            for Line in BBox:
                location = coordinateChange(Image, Layout, Line)
                BBoxes.append(location)
        else:
            BBoxes.append(location.copy())

    return BBoxes

