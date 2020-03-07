from semseg.text.textExtraction import TextExtraction
from semseg.image.imageExtraction import ImageExtraction
from semseg.table.tableExtraction import TableExtraction

from utils.logging.syslog import Logger

import sys
sys.dont_write_bytecode = True

class SemanticSegmentation():
    def __init__(self, conf, PagesImage, PagesLayout):
        self.configList = conf
        self.PagesImage = PagesImage
        self.PagesLayout = PagesLayout
        self.Page = len(PagesImage)
        self.Segmentation()

    def Segmentation(self):
        logging = Logger(__name__)
        Logger.get_log(logging).info('Segmentation Start')

        TextLevel = self.configList.text_level
        TableLevel = self.configList.table_level

        # for index in range(self.Page):
        #     PageImage = self.PagesImage[index]
        #     PageLayout = self.PagesLayout[index]

            # from semseg.text.level_2.tools import half_full_judge, BlockStartX
            # hf = half_full_judge(PageLayout)
            # BlockStartX(PageLayout, hf)
            #
            # from utils.formatChange.visualize.originLayout import layoutImage
            # import cv2
            # ImageSize = PageImage.shape
            # LayoutWidth = PageLayout.width
            # LayoutHeight = PageLayout.height
            # liRatio = [LayoutWidth / ImageSize[1], LayoutHeight / ImageSize[0]]
            #
            # image = layoutImage(PageImage,PageLayout,liRatio)
            #
            # height, width = image.shape[:2]
            # size = (int(height * 0.8), int(width * 1.2))
            # PageImage = cv2.resize(image, size)
            #
            # cv2.imshow('1', PageImage)
            # cv2.waitKey(0)

        if not self.configList.tit_choice:
            self.Text = TextExtraction(TextLevel, self.PagesLayout)
            self.Image = ImageExtraction(self.PagesLayout)
            self.Table = TableExtraction(TableLevel, self.PagesLayout)

        elif self.configList.tit_choice == 1:
            self.Text = TextExtraction(TextLevel, self.PagesLayout)

        elif self.configList.tit_choice == 2:
            self.Image = ImageExtraction(self.PagesLayout)

        elif self.configList.tit_choice == 3:
            self.Table = TableExtraction(TableLevel, self.PagesLayout)

        Logger.get_log(logging).info('Segmentation Finished')
        logging.logger.handlers.clear()
