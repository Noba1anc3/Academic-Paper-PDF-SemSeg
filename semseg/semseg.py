from semseg.text.ImgTabOut import *
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
        self.PgHeight = PagesLayout[0].height
        self.Page = len(PagesImage)
        self.Segmentation()

    def Segmentation(self):
        logging = Logger(__name__)
        Logger.get_log(logging).info('Segmentation Start')

        TextLevel = self.configList.text_level
        TableLevel = self.configList.table_level

        if not self.configList.tit_choice:
            self.Table = TableExtraction(TableLevel, self.PagesLayout)
            self.Image = ImageExtraction(self.PagesImage, self.PagesLayout)
            self.Text = TextExtraction(TextLevel, self.PagesLayout)
            self.Text.Text = ImgTabOut(self.PgHeight, self.Text.Text, self.Image.Image, self.Table.Table)
            self.Text.TableNote = TableOut(self.PgHeight, self.Text.TableNote, self.Table.Table)

        elif self.configList.tit_choice == 1:
            self.Text = TextExtraction(TextLevel, self.PagesLayout)

        elif self.configList.tit_choice == 2:
            self.Image = ImageExtraction(self.PagesLayout)

        elif self.configList.tit_choice == 3:
            self.Table = TableExtraction(TableLevel, self.PagesLayout)

        Logger.get_log(logging).info('Segmentation Finished')
        logging.logger.handlers.clear()
