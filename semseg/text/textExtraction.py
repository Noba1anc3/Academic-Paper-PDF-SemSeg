from semseg.text.level_1.Leve1Extraction import Leve1Extraction
from semseg.text.level_2.notetools import *
from semseg.text.level_2.maintext import *
from semseg.text.level_2.author import AuthorExtraction
from semseg.text.level_2.title import TitleExtraction
from semseg.text.level_2.page import PageExtraction
from semseg.text.level_2.note import NoteExtraction
from utils.logging.syslog import Logger

class TextExtraction():
    def __init__(self, TextLevel, PagesLayout):
        self.Text = []
        self.Title = []
        self.Author = []
        self.Page = []
        self.Note = []
        self.FigureNote = []
        self.TableNote = []

        self.TextLevel = TextLevel
        self.PagesLayout = PagesLayout
        self.Segmentation()

    def Segmentation(self):
        FigNoteList = []
        TabNoteList = []

        for PageNo in range(len(self.PagesLayout)):
            PageLayout = self.PagesLayout[PageNo]

            if self.TextLevel == 1:
                Text = Leve1Extraction(PageLayout)
                self.Text.append(Text)

            elif self.TextLevel == 2:
                Page, pgIndex = PageExtraction(PageLayout)
                Note, ntIndex = NoteExtraction(PageLayout)

                FigNoteList.append(FigureNoteExtraction(PageLayout))
                TabNoteList.append( TableNoteExtraction(PageLayout))

                if PageNo == 0:
                    Title,  ttIndex = TitleExtraction(PageLayout)
                    Author, auIndex = AuthorExtraction(PageLayout, ttIndex)
                    self.Title.append(Title)
                    self.Author.append(Author)
                else:
                    ttIndex = -1
                    auIndex = []
                    self.Title.append([])
                    self.Author.append([])

                Text = Level2Extraction(PageLayout, pgIndex, ntIndex, ttIndex, auIndex)

                self.Page.append(Page)
                self.Note.append(Note)
                self.Text.append(Text)

        self.FigureNote = NotePostProcess(FigNoteList, "F")
        self.TableNote  = NotePostProcess(TabNoteList, "T")

        self.Text = FigTabNoteOut(self.Text, self.TableNote, self.FigureNote)

        logging = Logger(__name__)
        Logger.get_log(logging).info('Text Segmentation Finished')
        logging.logger.handlers.clear()
