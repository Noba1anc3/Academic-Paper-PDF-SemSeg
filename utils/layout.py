from pdfminer.layout import *
from layout import *
import cv2

def add_box(image, LTType, item_boxes, li_ratio_h, li_ratio_w):
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


def drawBox(image, LTType, Boxes):
    Text = False

    if LTType == LTTitle:                  #red
        color = (0, 0, 255)
        typeText = 'Title'
    elif LTType == LTAuthor:               #green
        color = (0, 255,0)
        typeText = 'Author'
    elif LTType == LTLine:                 #yellow
        color = (0, 255, 255)
    elif LTType == LTFigure:               #blue
        color = (255, 0, 0)
    elif LTType == LTRect:                 #darkvoilet
        color = (211, 0, 148)
    elif LTType == LTCurve:                #darkcyan
        color = (139, 139, 0)

    for Box in Boxes:
        leftTop = (Box[0], Box[1])
        rightDown = (Box[2], Box[3])
        cv2.rectangle(image, leftTop, rightDown, color, 3)
        if not Text:
            cv2.putText(image, typeText, (Box[0], Box[1]), 0, 1.5, color, thickness=3)
            Text = True

    return image


def get_liRatio(PageImage, PageLayout):
    IMG_H = PageImage.shape[0]
    IMG_W = PageImage.shape[1]
    LAYOUT_H = PageLayout.y1
    LAYOUT_W = PageLayout.x1
    liRatioH = LAYOUT_H / IMG_H
    liRatioW = LAYOUT_W / IMG_W

    return [liRatioW, liRatioH]

def getBoundingBoxes(LAYOUT_H, BBoxList, liRatio):
    BBoxes = []
    SafeCheck = False

    for BBox in BBoxList:
        XleftUp = int(BBox.x0 / liRatio[0])
        YleftUp = int((LAYOUT_H - BBox.y1) / liRatio[1])
        XrightDown = int(BBox.x1 / liRatio[0])
        YrightDown = int((LAYOUT_H - BBox.y0) / liRatio[1])

        if SafeCheck:
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

        for Item in BBox:
            XleftUp = int(Item.x0 / liRatio[0])
            YleftUp = int((LAYOUT_H - Item.y1) / liRatio[1])
            XrightDown = int(Item.x1 / liRatio[0])
            YrightDown = int((LAYOUT_H - Item.y0) / liRatio[1])
            BBoxes.append([XleftUp, YleftUp, XrightDown, YrightDown])

    return BBoxes

def layoutImage(PageImage, PageLayout, liRatio):
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