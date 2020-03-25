from semseg.text.level_2.image_note import *
from semseg.text.level_2.notetools import NotePostProcess
from semseg.image.image import ImgExtraction
from utils.logging.syslog import Logger

class ImageExtraction():
    def __init__(self, PagesImage, PagesLayout):
        self.Image = []
        self.PagesImage = PagesImage
        self.PagesLayout = PagesLayout
        self.Segmentation()

    def Segmentation(self):
        self.FNoteExtract()

        for PageNo in range(len(self.PagesLayout)):
            PageImage = self.PagesImage[PageNo]
            PageLayout = self.PagesLayout[PageNo]
            PageFNote = self.FigureNotes[PageNo]

            Image = ImgExtraction(PageImage, PageLayout, PageFNote)
            self.Image.append(Image)

        logging = Logger(__name__)
        Logger.get_log(logging).info('Image Segmentation Finished')
        logging.logger.handlers.clear()

    def FNoteExtract(self):
        FigNoteList = []

        for PageNo in range(len(self.PagesLayout)):
            PageLayout = self.PagesLayout[PageNo]
            FigNoteList.append(FigureNoteExtraction(PageLayout))

        self.FigureNotes = NotePostProcess(FigNoteList, 'F')
