from semseg.text.image_note import FigureNoteExtraction
from semseg.text.table_note import TableNoteExtraction
from semseg.text.author import AuthorExtraction
from semseg.text.title import TitleExtraction
from semseg.text.note import *

from utils.formatChange.visualize.annotate import *
import numpy as np

class SemanticSegmentation():
    def __init__(self, conf, PagesImage, PagesLayout):
        self.Text = []
        self.Image = []
        self.Table = []
        self.configList = conf
        self.PagesImage = PagesImage
        self.PagesLayout = PagesLayout
        self.Segmentation()

    def Segmentation(self):
        withPageNo = False
        FileFNoteType = []
        FileTNoteType = []
        PageType = half_full_judge(self.PagesLayout[0])

        textLevel = self.configList.text_level
        tableLevel = self.configList.table_level
        TITchoice = self.configList.tit_choice

        for PageNo in range(len(self.PagesImage)):
            PageImage = self.PagesImage[PageNo]
            PageLayout = self.PagesLayout[PageNo]

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
