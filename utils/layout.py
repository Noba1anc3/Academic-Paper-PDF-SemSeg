from pdfminer.layout import *
from layout import *
import cv2

def drawBox(image, LTType, Boxes):
    #在image图像上根据LTType绘制相应颜色的检测框，并在左上角附上其所属的类型
    #Boxes由若干个Box组成，第一个Box为该类型所有小区域所形成的大区域，后面的Box分别是该类型下所有的小区域
    #每一个Box由四个整数组成，分别是左上角的横坐标，左上角的纵坐标，右下角的横坐标，右下角的纵坐标

    Text = False

    if LTType == LTTitle:                  #red
        color = (0, 0, 255)
        typeText = 'Title'
    elif LTType == LTAuthor:               #green
        color = (0, 255,0)
        typeText = 'Author'
    elif LTType == LTPageNo:               #yellow
        color = (0, 255, 255)
        typeText = 'PageNo'
    elif LTType == LTNote:                 #blue
        color = (255, 0, 0)
        typeText = 'Note'
    elif LTType == LTFigure:               #slateblue
        color = (238, 103, 122)
        typeText = 'Figure'
    elif LTType == LTFigureNote:           #darkvoilet
        color = (211, 0, 148)
        typeText = 'FigureNote'
    elif LTType == LTTableNote:            #darkcyan
        color = (139, 139, 0)
        typeText = 'TableNote'

    if LTType == LTFigureNote or LTType == LTTableNote:
        for Box in Boxes:
            Text = False
            for Line in Box:
                leftTop = (Line[0], Line[1])
                rightDown = (Line[2], Line[3])
                cv2.rectangle(image, leftTop, rightDown, color, 3)
                if not Text:
                    cv2.putText(image, typeText, (Line[0], Line[1]), 0, 1.5, color, thickness=3)
                    Text = True
        return image
    else:
        if LTType == LTFigure:
            index = 1
        else:
            index = 0

        for i in range(index, len(Boxes)):
            Box = Boxes[i]
            leftTop = (Box[0], Box[1])
            rightDown = (Box[2], Box[3])
            cv2.rectangle(image, leftTop, rightDown, color, 3)
            if not Text or index == 1:
                cv2.putText(image, typeText, (Box[0], Box[1]), 0, 1.5, color, thickness=3)
                Text = True
        return image

def overlap(lineA, lineB):
    lengthA = lineA[1] - lineA[0]
    lengthB = lineB[1] - lineB[0]

    if lineA[1] <= lineB[0]:
        return 0
    if lineA[0] >= lineB[1]:
        return 0
    if lineA[0] <= lineB[0] and lineB[1] <= lineA[1]:
        return 1
    if lineB[0] <= lineA[0] and lineA[1] <= lineB[1]:
        return 1

    lap = lineA[1] - lineB[0]
    if lap < min(lengthA, lengthB):
        return lap/min(lengthA, lengthB)
    else:
        lap = lineB[1] - lineA[0]
        return lap/min(lengthA, lengthB)

def get_liRatio(PageImage, PageLayout):
    #计算pdfminer分析出来的layout和pdf2image生成的image之间的尺寸比
    IMG_H = PageImage.shape[0]
    IMG_W = PageImage.shape[1]
    LAYOUT_H = PageLayout.y1
    LAYOUT_W = PageLayout.x1
    liRatioH = LAYOUT_H / IMG_H
    liRatioW = LAYOUT_W / IMG_W

    return [liRatioW, liRatioH]

def NoteBoundingBoxes(LAYOUT_H, BBoxList, liRatio):
    # 针对图注类型特殊处理的计算其BBoxes的方法，其中BBoxList的每一项为一个列表
    # 每一个列表都是一个图注，列表内部由若干个LTTextLineHorizontal组成

    BBoxes = []
    for index in range(len(BBoxList)):
        Block = BBoxList[index]
        SafeCheck = False
        BBoxes.append([])
        for Line in Block:
            XleftUp = int(Line.x0 / liRatio[0])
            YleftUp = int((LAYOUT_H - Line.y1) / liRatio[1])
            XrightDown = int(Line.x1 / liRatio[0])
            YrightDown = int((LAYOUT_H - Line.y0) / liRatio[1])

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
                BBoxes[index].append([XleftUp, YleftUp, XrightDown, YrightDown])

            BBoxes[index].append([XleftUp, YleftUp, XrightDown, YrightDown])

    return BBoxes

def getBoundingBoxes(LAYOUT_H, BBoxList, liRatio):
    #根据Layout的高度和liRatio将从Layout提取出来的坐标转换为Image上的坐标
    #传入进来的BBoxList或者由若干个LTTextBoxHorizontal组成，或者由若干个LTTextLineHorizontal组成
    #该方法根据从Layout中提取出来的BBoxList生成用于标注图片的BBoxes列表并返回

    BBoxes = []
    SafeCheck = False

    for BBox in BBoxList:
        #由于pdfminer的内部问题，Layout.Height - Box.y1才是该Box正确的左上角纵坐标
        #同理Box正确的右下角纵坐标为Layout.Height - Box.y0
        XleftUp = int(BBox.x0 / liRatio[0])
        YleftUp = int((LAYOUT_H - BBox.y1) / liRatio[1])
        XrightDown = int(BBox.x1 / liRatio[0])
        YrightDown = int((LAYOUT_H - BBox.y0) / liRatio[1])

        if SafeCheck:
            #该目的为确定出所有LTTextBoxHorizontal所组成的大区域并置为该方法返回的BBoxes的第一项
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
            BBoxes.append([XleftUp, YleftUp, XrightDown, YrightDown])

        if isinstance(BBox, LTTextBoxHorizontal):
            for Item in BBox:
                XleftUp = int(Item.x0 / liRatio[0])
                YleftUp = int((LAYOUT_H - Item.y1) / liRatio[1])
                XrightDown = int(Item.x1 / liRatio[0])
                YrightDown = int((LAYOUT_H - Item.y0) / liRatio[1])
                BBoxes.append([XleftUp, YleftUp, XrightDown, YrightDown])
        else:
            BBoxes.append([XleftUp, YleftUp, XrightDown, YrightDown])

    return BBoxes

def add_box(image, LTType, item_boxes, li_ratio_h, li_ratio_w):
    #暂时弃用
    if LTType == LTTextBoxHorizontal:      #red
        color = (0, 0, 255)
    elif LTType == LTTextLineHorizontal:   #green
        color = (0, 255,0)
    elif LTType == LTLine:                 #yellow
        color = (0, 255, 255)
    elif LTType == LTFigure:               #blue
        color = (255, 0, 0)
    elif LTType == LTRect:                 #darkvoilet
        color = (211, 0, 148)
    elif LTType == LTCurve:                #darkcyan
        color = (139, 139, 0)

    leftUpX = item_boxes[0] / li_ratio_w
    leftUpY = item_boxes[1] / li_ratio_h
    rightDownX = item_boxes[2] / li_ratio_w
    rightDownY = item_boxes[3] / li_ratio_h

    leftTop = (int(leftUpX), int(rightDownY))
    rightDown = (int(rightDownX), int(leftUpY))

    cv2.rectangle(image, leftTop, rightDown, color, 3)

    return image

def layoutImage(PageImage, PageLayout, liRatio):
    #暂时弃用
    LAYOUT_H = PageLayout.y1
    liRatioW = liRatio[0]
    liRatioH = liRatio[1]
    for layoutItem in PageLayout:
        XleftUp = layoutItem.x0
        YleftUp = LAYOUT_H - layoutItem.y0
        XrightDown = layoutItem.x1
        YrightDown = LAYOUT_H - layoutItem.y1
        BoundingBox = [XleftUp, YleftUp, XrightDown, YrightDown]

        if isinstance(layoutItem, LTTextBoxHorizontal):
            for textline in layoutItem:
                if isinstance(textline, LTTextLineHorizontal):
                    TextLine = [textline.x0, LAYOUT_H - textline.y0, textline.x1, LAYOUT_H - textline.y1]
                    PageImage = add_box(PageImage, LTTextLineHorizontal, TextLine, liRatioH, liRatioW)
                else:
                    print(str(type(textline)) + 'in LTTextBoxHorizontal')
            PageImage = add_box(PageImage, LTTextBoxHorizontal, BoundingBox, liRatioH, liRatioW)

        elif isinstance(layoutItem, LTLine):
            PageImage = add_box(PageImage, LTLine, BoundingBox, liRatioH, liRatioW)

        elif isinstance(layoutItem, LTTextLineHorizontal):
            PageImage = add_box(PageImage, LTTextLineHorizontal, BoundingBox, liRatioH, liRatioW)

        elif isinstance(layoutItem, LTFigure):
            PageImage = add_box(PageImage, LTFigure, BoundingBox, liRatioH, liRatioW)

        elif isinstance(layoutItem, LTRect):
            PageImage = add_box(PageImage, LTRect, BoundingBox, liRatioH, liRatioW)

        elif isinstance(layoutItem, LTCurve):
            PageImage = add_box(PageImage, LTCurve, BoundingBox, liRatioH, liRatioW)

        else:
            print(str(type(layoutItem)) + 'in LTPage')

    return PageImage