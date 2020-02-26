from pdfminer.layout import *
from utils.formatChange.visualize.Layout import *

import cv2

class PageVisualize():
    def __init__(self, Image, Layout):
        self.Image = Image
        self.IMG_SIZE = Image.shape
        self.LayoutHeight = Layout.height
        self.LayoutWidth  = Layout.width
        self.liRatio = [self.LayoutWidth / self.IMG_SIZE[1], self.LayoutHeight / self.IMG_SIZE[0]]

    def annotate(self, LTType, LTBBoxes):
        if LTType == LTTableNote or LTType == LTFigureNote:
            ImageBBoxes = self.NoteBBoxes(LTBBoxes)
        else:
            ImageBBoxes = self.getBBoxes(LTBBoxes)

        self.drawBox(LTType, ImageBBoxes)

    def show(self):
        height, width = self.Image.shape[:2]
        size = (int(height * 0.8), int(width * 1.2))
        PageImage = cv2.resize(self.Image, size)
        cv2.imshow('img', PageImage)
        cv2.waitKey(0)

    def NoteBBoxes(self, LTBBoxes):
        # 针对图注类型特殊处理的计算其BBoxes的方法，其中BBoxList的每一项为一个列表
        # 每一个列表都是一个图注，列表内部由若干个LTTextLineHorizontal组成
        BBoxes = []
        for index in range(len(LTBBoxes)):
            Block = LTBBoxes[index]
            SafeCheck = False
            BBoxes.append([])
            for Line in Block:
                XleftUp = int(Line.x0 / self.liRatio[0])
                YleftUp = int((self.LayoutHeight - Line.y1) / self.liRatio[1])
                XrightDown = int(Line.x1 / self.liRatio[0])
                YrightDown = int((self.LayoutHeight - Line.y0) / self.liRatio[1])

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

    def getBBoxes(self, LTBBoxes):
        # 根据Layout的高度和liRatio将从Layout提取出来的坐标转换为Image上的坐标
        # 传入进来的BBoxList或者由若干个LTTextBoxHorizontal组成，或者由若干个LTTextLineHorizontal组成
        # 该方法根据从Layout中提取出来的BBoxList生成用于标注图片的BBoxes列表并返回

        BBoxes = []
        SafeCheck = False

        for BBox in LTBBoxes:
            # 由于pdfminer的内部问题，Layout.Height - Box.y1才是该Box正确的左上角纵坐标
            # 同理Box正确的右下角纵坐标为Layout.Height - Box.y0
            XleftUp = int(BBox.x0 / self.liRatio[0])
            YleftUp = int((self.LayoutHeight - BBox.y1) / self.liRatio[1])
            XrightDown = int(BBox.x1 / self.liRatio[0])
            YrightDown = int((self.LayoutHeight - BBox.y0) / self.liRatio[1])

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
                BBoxes.append([XleftUp, YleftUp, XrightDown, YrightDown])

            if isinstance(BBox, LTTextBoxHorizontal):
                for Item in BBox:
                    XleftUp = int(Item.x0 / self.liRatio[0])
                    YleftUp = int((self.LayoutHeight- Item.y1) / self.liRatio[1])
                    XrightDown = int(Item.x1 / self.liRatio[0])
                    YrightDown = int((self.LayoutHeight - Item.y0) / self.liRatio[1])
                    BBoxes.append([XleftUp, YleftUp, XrightDown, YrightDown])
            else:
                BBoxes.append([XleftUp, YleftUp, XrightDown, YrightDown])

        return BBoxes

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

        if LTType == LTFigureNote or LTType == LTTableNote:
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
            if LTType == LTFigure:
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
