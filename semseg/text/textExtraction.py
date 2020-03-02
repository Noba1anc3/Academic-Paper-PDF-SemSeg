from semseg.text.level_1.Leve1Extraction import Leve1Extraction
from semseg.text.level_2.image_note import FigureNoteExtraction
from semseg.text.level_2.table_note import TableNoteExtraction
from semseg.text.level_2.author import AuthorExtraction
from semseg.text.level_2.title import TitleExtraction
from semseg.text.level_2.note import *
from semseg.text.level_2.tools import *
from utils.logging.syslog import Logger

import sys
sys.dont_write_bytecode = True

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
        FileFNoteType = []
        FileTNoteType = []
        PageType = half_full_judge(self.PagesLayout[0])

        for PageNo in range(len(self.PagesLayout)):
            PageLayout = self.PagesLayout[PageNo]

            if self.TextLevel == 1:
                Text = Leve1Extraction(PageLayout)
                self.Text.append(Text)
            else:
                Page, Note = NoteExtraction(PageLayout, PageType)
                FigNote, FileFNoteType = FigureNoteExtraction(PageLayout, FileFNoteType)
                TabNote, FileTNoteType = TableNoteExtraction(PageLayout, FileTNoteType)

                if PageNo == 0:
                    Title, titleIndex = TitleExtraction(PageLayout)
                    Author = AuthorExtraction(PageLayout, titleIndex)
                    self.Title.append(Title)
                    self.Author.append(Author)
                else:
                    self.Title.append([])
                    self.Author.append([])

                self.Page.append(Page)
                self.Note.append(Note)
                self.FigureNote.append(FigNote)
                self.TableNote.append(TabNote)

        logging = Logger(__name__)
        Logger.get_log(logging).info('Text Segmentation Finished')
        logging.logger.handlers.clear()
