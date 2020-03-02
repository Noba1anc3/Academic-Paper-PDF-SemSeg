from semseg.image.image import ImgExtraction
from utils.logging.syslog import Logger
import sys
sys.dont_write_bytecode = True

class ImageExtraction():
    def __init__(self, PagesLayout):
        self.Image = []
        self.PagesLayout = PagesLayout
        self.Segmentation()

    def Segmentation(self):
        for PageNo in range(len(self.PagesLayout)):
            PageLayout = self.PagesLayout[PageNo]
            Image = ImgExtraction(PageLayout)
            self.Image.append(Image)


        logging = Logger(__name__)
        Logger.get_log(logging).info('Image Segmentation Finished')
        logging.logger.handlers.clear()