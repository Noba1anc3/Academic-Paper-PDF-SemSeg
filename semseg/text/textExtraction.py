from semseg.text.subExtract.image_note import FigureNoteExtraction
from semseg.text.subExtract.table_note import TableNoteExtraction
from semseg.text.subExtract.author import AuthorExtraction
from semseg.text.subExtract.title import TitleExtraction
from semseg.text.subExtract.note import *
from semseg.text.subExtract.tools import *

from utils.formatChange.visualize.annotate import *

class TextExtraction():
    def __init__(self, TextLevel, PagesImage, PagesLayout):
        self.Text = []
        self.TextLevel = TextLevel
        self.PagesImage = PagesImage
        self.PagesLayout = PagesLayout
        self.Segmentation()

    def Segmentation(self):
        withPageNo = False
        FileFNoteType = []
        FileTNoteType = []
        PageType = half_full_judge(self.PagesLayout[0])

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
