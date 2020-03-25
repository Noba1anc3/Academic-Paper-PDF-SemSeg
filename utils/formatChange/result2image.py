
from utils.formatChange.visualize.annotate import *

def rst2image(conf, semseg, PagesImage, PagesLayout):
    TIT = conf.tit_choice
    TextLevel = conf.text_level
    TableLevel = conf.table_level
    ImageList = []

    if TIT == 0 or TIT == 1:
        if TextLevel == 1:
            Text = semseg.Text.Text
        else:
            Text = semseg.Text.Text
            Title = semseg.Text.Title
            Author = semseg.Text.Author
            Page = semseg.Text.Page
            Note = semseg.Text.Note
            FigureNote = semseg.Text.FigureNote
            TableNote = semseg.Text.TableNote
        if TIT == 0:
            Image = semseg.Image.Image
            Table = semseg.Table.Table
            Column_Header = semseg.Table.Column_Header
            Row_Header = semseg.Table.Row_Header
            Body = semseg.Table.Body

    elif TIT == 2:
        Image = semseg.Image.Image
    else:
        Table = semseg.Table.Table
        Column_Header = semseg.Table.Column_Header
        Row_Header = semseg.Table.Row_Header
        Body = semseg.Table.Body

    for index in range(len(PagesImage)):
        PageImage = PagesImage[index]
        PageLayout = PagesLayout[index]

        PV = PageVisualize(PageImage, PageLayout)

        if TIT == 0 or TIT == 1:
            if TextLevel == 1:
                PageVisualize.annotate(PV, LTText, Text[index])
            else:
                PageVisualize.annotate(PV, LTText, Text[index])
                PageVisualize.annotate(PV, LTTitle, Title[index])
                PageVisualize.annotate(PV, LTAuthor, Author[index])
                PageVisualize.annotate(PV, LTPageNo, Page[index])
                PageVisualize.annotate(PV, LTNote, Note[index])
                PageVisualize.annotate(PV, LTFigureNote, FigureNote[index])
                PageVisualize.annotate(PV, LTTableNote, TableNote[index])
            if TIT == 0:
                PageVisualize.annotate(PV, LTFigure, Image[index])
                PageVisualize.annotate(PV, LTTable, Table[index])
                if TableLevel == 2:
                    PageVisualize.annotate(PV, LTCell, Column_Header[index])
                    PageVisualize.annotate(PV, LTCell, Row_Header[index])
                    PageVisualize.annotate(PV, LTCell, Body[index])

        elif TIT == 2:
            PageVisualize.annotate(PV, LTFigure, Image[index])
        else:
            PageVisualize.annotate(PV, LTTable, Table[index])
            if TableLevel == 2:
                PageVisualize.annotate(PV, LTCell, Column_Header[index])
                PageVisualize.annotate(PV, LTCell, Row_Header[index])
                PageVisualize.annotate(PV, LTCell, Body[index])

        #PageVisualize.show(PV)
        ImageList.append(PV.Image)

        # if index < len(PagesImage) - 1:
        #     cv2.waitKey(0)

    return ImageList