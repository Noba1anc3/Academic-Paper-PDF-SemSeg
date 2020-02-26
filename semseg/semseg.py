from semseg.text.image_note import FigureNoteExtraction
from semseg.text.table_note import TableNoteExtraction
from semseg.text.author import AuthorExtraction
from semseg.text.title import TitleExtraction
from semseg.text.note import *
from utils.formatChange.visualize.annotate import *
import numpy as np

class SemanticSegmentation():
    def __init__(self, PagesImage, PagesLayout, configList):
        self.PagesImage = PagesImage
        self.PagesLayout = PagesLayout
        self.configList = configList
        self.Segmentation()

    def Segmentation(self):
        withPageNo = False
        FileFNoteType = []
        FileTNoteType = []
        PageType = half_full_judge(self.PagesLayout[0])

        textLevel = self.configList[3]
        tableLevel = self.configList[4]
        TITchoice = self.configList[5]

        for PageNo in range(len(self.PagesImage)):
            PageImage = self.PagesImage[PageNo]
            PageLayout = self.PagesLayout[PageNo]
            PageImage = cv2.cvtColor(np.asarray(PageImage), cv2.COLOR_RGB2BGR)

            PV = PageVisualize(PageImage, PageLayout)
            Page, Note = NoteExtraction(PageLayout, PageType)

            if PageNo == 0:
                Title, titleIndex = TitleExtraction(PageLayout)
                PageVisualize.annotate(PV, LTTitle, Title)
                Author = AuthorExtraction(PageLayout, titleIndex)
                PageVisualize.annotate(PV, LTAuthor, Author)
                if not len(Page) == 0:
                    withPageNo = True

            if withPageNo:
                PageVisualize.annotate(PV, LTPageNo, Page)

            PageVisualize.annotate(PV, LTNote, Note)
            Figure, FigNote, FileFNoteType = FigureNoteExtraction(PageLayout, FileFNoteType)
            TabNote, FileTNoteType = TableNoteExtraction(PageLayout, FileTNoteType)
            PageVisualize.annotate(PV, LTFigure, Figure)
            PageVisualize.annotate(PV, LTFigureNote, FigNote)
            PageVisualize.annotate(PV, LTTableNote, TabNote)

            PageVisualize.show(PV)
