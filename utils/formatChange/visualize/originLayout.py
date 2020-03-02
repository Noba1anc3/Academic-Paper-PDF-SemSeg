from pdfminer.layout import *
import cv2
import sys

sys.dont_write_bytecode = True

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