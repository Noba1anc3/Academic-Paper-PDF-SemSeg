from semseg.text.subExtract.image_note import FigureNoteExtraction
from semseg.text.subExtract.table_note import TableNoteExtraction
from semseg.text.subExtract.author import AuthorExtraction
from semseg.text.subExtract.title import TitleExtraction
from semseg.text.subExtract.note import *
from semseg.text.subExtract.tools import *

class TextExtraction():
    def __init__(self, TextLevel, PagesImage, PagesLayout):
        self.Text = []
        self.Title = []
        self.Author = []
        self.Page = []
        self.Note = []
        self.FigureNote = []
        self.TableNote = []

        self.TextLevel = TextLevel
        self.PagesImage = PagesImage
        self.PagesLayout = PagesLayout
        self.Segmentation()

    def Segmentation(self):
        FileFNoteType = []
        FileTNoteType = []
        PageType = half_full_judge(self.PagesLayout[0])

        for PageNo in range(len(self.PagesImage)):
            PageLayout = self.PagesLayout[PageNo]

            Page, Note = NoteExtraction(PageLayout, PageType)
            self.Page.append(Page)
            self.Note.append(Note)
            if PageNo == 0:
                Title, titleIndex = TitleExtraction(PageLayout)
                Author = AuthorExtraction(PageLayout, titleIndex)
                self.Title.append(Title)
                self.Author.append(Author) 

            Figure, FigNote, FileFNoteType = FigureNoteExtraction(PageLayout, FileFNoteType)
            TabNote, FileTNoteType = TableNoteExtraction(PageLayout, FileTNoteType)
            self.FigureNote.append(FigNote)
            self.TableNote.append(TabNote)
            self.Title.append([])
            self.Author.append([])

