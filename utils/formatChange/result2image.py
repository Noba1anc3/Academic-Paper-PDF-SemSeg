
from utils.formatChange.visualize.annotate import *

def rst2image(conf, semseg, PagesImage, PagesLayout):
    TIT = conf.tit_choice
    TextLevel = conf.text_level
    TableLevel = conf.table_level

    if TIT == 0 or TIT == 1:
        if TextLevel == 1:
            Text = semseg.Text.Text
        else:
            Title = semseg.Text.Title
            Author = semseg.Text.Author
            Page = semseg.Text.Page
            Note = semseg.Text.Note
            FigureNote = semseg.Text.FigureNote
            TableNote = semseg.Text.TableNote
        if TIT == 0:
            Image = semseg.Image.Image
    elif TIT == 2:
        Image = semseg.Image.Image
    else:
        pass

    for index in range(len(PagesImage)):
        PageImage = PagesImage[index]
        PageLayout = PagesLayout[index]

        PV = PageVisualize(PageImage, PageLayout)

        if TIT == 0 or TIT == 1:
            if TextLevel == 1:
                PageVisualize.annotate(PV, LTText, Text[index])
            else:
                PageVisualize.annotate(PV, LTTitle, Title[index])
                PageVisualize.annotate(PV, LTAuthor, Author[index])
                PageVisualize.annotate(PV, LTPageNo, Page[index])
                PageVisualize.annotate(PV, LTNote, Note[index])
                PageVisualize.annotate(PV, LTFigureNote, FigureNote[index])
                PageVisualize.annotate(PV, LTTableNote, TableNote[index])
            if TIT == 0:
                PageVisualize.annotate(PV, LTFigure, Image[index])
                if TableLevel == 1:
                    pass
                else:
                    pass
        elif TIT == 2:
            PageVisualize.annotate(PV, LTFigure, Image[index])
        else:
            if TableLevel == 1:
                pass
            else:
                pass

        PageVisualize.show(PV)

        if index < len(PagesImage) - 1:
            cv2.waitKey(0)

    return PagesImage