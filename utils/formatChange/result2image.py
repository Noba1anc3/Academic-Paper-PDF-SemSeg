
from utils.formatChange.visualize.annotate import *

def rst2image(semseg, PagesImage, PagesLayout):
    Title = semseg.Text.Title
    Author = semseg.Text.Author
    Page = semseg.Text.Page
    Note = semseg.Text.Note
    FigureNote = semseg.Text.FigureNote
    TableNote = semseg.Text.TableNote

    for index in range(len(PagesImage)):
        PageImage = PagesImage[index]
        PageLayout = PagesLayout[index]

        PV = PageVisualize(PageImage, PageLayout)
        PageVisualize.annotate(PV, LTTitle, Title[index])
        PageVisualize.annotate(PV, LTTitle, Author[index])
        PageVisualize.annotate(PV, LTPageNo, Page[index])
        PageVisualize.annotate(PV, LTNote, Note[index])
        #PageVisualize.annotate(PV, LTFigure, Figure)
        PageVisualize.annotate(PV, LTFigureNote, FigureNote[index])
        PageVisualize.annotate(PV, LTTableNote, TableNote[index])
        PageVisualize.show(PV)

    return PagesImage