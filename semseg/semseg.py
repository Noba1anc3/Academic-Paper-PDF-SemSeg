from semseg.text.image_note import FigureNoteExtraction
from semseg.text.table_note import TableNoteExtraction
from semseg.text.author import AuthorExtraction
from semseg.text.title import TitleExtraction
from semseg.text.note import *
from utils.postProcess.visualize.annotate import *
import numpy as np

def Segmentation(PagesImage, PagesLayout):
    withPageNo = False
    FileFNoteType = []
    FileTNoteType = []
    PageType = half_full_judge(PagesLayout[0])

    for PageNo in range(len(PagesImage)):
        PageImage = PagesImage[PageNo]
        PageLayout = PagesLayout[PageNo]
        PageImage = cv2.cvtColor(np.asarray(PageImage), cv2.COLOR_RGB2BGR)

        liRatio = get_liRatio(PageImage, PageLayout)
        PV = PageVisualize(PageImage, PageLayout.height, liRatio)
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
