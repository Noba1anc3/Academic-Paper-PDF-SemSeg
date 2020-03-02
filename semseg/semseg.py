from semseg.text.textExtraction import TextExtraction
from semseg.image.imageExtraction import ImageExtraction
from semseg.table.tableExtraction import TableExtraction

from utils.logging.syslog import Logger

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

        if not self.configList.tit_choice:
            self.Text = TextExtraction(TextLevel, self.PagesLayout)
            self.Image = ImageExtraction(self.PagesLayout)
            self.Table = TableExtraction(TableLevel, self.PagesLayout)

        elif self.configList.tit_choice == 1:
            self.Text = TextExtraction(TextLevel, self.PagesLayout)

        elif self.configList.tit_choice == 2:
            self.Image = ImageExtraction(self.PagesLayout)

        else:
            self.Table = TableExtraction(TableLevel, self.PagesLayout)

        Logger.get_log(logging).info('Segmentation Finished')
        logging.logger.handlers.clear()
