from semseg.text.level_2.image_note import *
from semseg.text.level_2.notetools import NotePostProcess
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
        self.FNoteExtract()

        for PageNo in range(len(self.PagesLayout)):
            PageLayout = self.PagesLayout[PageNo]
            PageFNote = self.FigureNotes[PageNo]

            Image = ImgExtraction(PageLayout, PageFNote)
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
