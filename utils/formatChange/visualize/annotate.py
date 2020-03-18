from utils.formatChange.visualize.Layout import *
from utils.formatChange.coordinateChange import *

import cv2
import sys

sys.dont_write_bytecode = True

class PageVisualize():
    def __init__(self, Image, Layout):
        self.Image = Image
        self.Layout = Layout

    def annotate(self, LTType, LTBBoxes):
        if LTType == LTTableNote or LTType == LTFigureNote or LTType == LTText or LTType == LTNote:
            ImageBBoxes = NoteBBoxes(self.Layout, LTBBoxes)
        else:
            ImageBBoxes = getBBoxes(self.Layout, LTBBoxes)

        self.drawBox(LTType, ImageBBoxes)

    def show(self):
        height, width = self.Image.shape[:2]
        size = (int(height * 0.8), int(width * 1.2))
        PageImage = cv2.resize(self.Image, size)
        cv2.imshow('img', PageImage)
        cv2.waitKey(0)

    def drawBox(self, LTType, Boxes):
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
        elif LTType == LTText:
            color = (148, 238, 78)             #seagreen
            typeText = 'Text'
        elif LTType == LTTable:
            color = (0, 140, 255)              #darkorange
            typeText = 'Table'

        if LTType == LTFigureNote or LTType == LTTableNote or LTType == LTText or LTType == LTNote:
            for Box in Boxes:
                Text = False
                for Line in Box:
                    leftTop = (Line[0], Line[1])
                    rightDown = (Line[2], Line[3])
                    cv2.rectangle(self.Image, leftTop, rightDown, color, 3)
                    if not Text:
                        cv2.putText(self.Image, typeText, (Line[0], Line[1]), 0, 1.5, color, thickness=3)
                        Text = True

        else:
            if LTType == LTFigure or LTType == LTTable:
                index = 1
            else:
                index = 0

            for i in range(index, len(Boxes)):
                Box = Boxes[i]
                leftTop = (Box[0], Box[1])
                rightDown = (Box[2], Box[3])
                cv2.rectangle(self.Image, leftTop, rightDown, color, 3)
                if not Text or index == 1:
                    cv2.putText(self.Image, typeText, (Box[0], Box[1]), 0, 1.5, color, thickness=3)
                    Text = True

