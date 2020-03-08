import sys
from utils.formatChange.coordinateChange import *

sys.dont_write_bytecode = True

def rst2json(conf, fileName, semseg, PagesImage, PagesLayout):
    TIT = conf.tit_choice
    TextLevel = conf.text_level

    L1Text = None
    Title = None
    Author = None
    Page = None
    Note = None
    FigureNote = None
    TableNote = None

    Figure = None
    Table = None

    JsonDict = {}
    JsonDict['FileName'] = fileName
    JsonDict['Pages'] = []

    if TIT == 0 or TIT == 1:
        if TextLevel == 1:
            L1Text = semseg.Text.Text
        else:
            Title = semseg.Text.Title
            Author = semseg.Text.Author
            Page = semseg.Text.Page
            Note = semseg.Text.Note
            FigureNote = semseg.Text.FigureNote
            TableNote = semseg.Text.TableNote
        if TIT == 0:
            Figure = semseg.Image.Image
    elif TIT == 2:
        Figure = semseg.Image.Image
    else:
        pass

    for page in range(semseg.Page):
        Image = PagesImage[page]
        Layout = PagesLayout[page]

        LTPage = {}
        LTPage['PageNo'] = page + 1
        LTPage['PageLayout'] = []
        PageLayout = {}

        if TIT == 0 or TIT == 1:
            PageLayout['Text'] = []
            if TIT == 0:
                PageLayout['Figure'] = []
                PageLayout['Table'] = []
        elif TIT == 2:
            PageLayout['Figure'] = []
        else:
            PageLayout['Table'] = []

        if 'Text' in PageLayout.keys():
            if TextLevel == 1:
                if not L1Text[page] == []:
                    TextItem = L1Text[page]
                    TextJson = L1TexT(Image, Layout, 'L1Text', TextItem)
                    PageLayout['Text'].append(TextJson)
            else:
                if not Title[page] == []:
                    TitleItem = Title[page]
                    TitleJson = L2Text(Image, Layout, 'Title', TitleItem)
                    PageLayout['Text'].append(TitleJson)
                if not Author[page] == []:
                    AuthorItem = Author[page][0]
                    AuthorJson = L2Text(Image, Layout, 'Author', AuthorItem)
                    PageLayout['Text'].append(AuthorJson)
                if not Page[page] == []:
                    PageItem = Page[page][0]
                    PageJson = L2Page(Image, Layout, 'Page', PageItem)
                    PageLayout['Text'].append(PageJson)
                if not Note[page] == []:
                    NoteItem = Note[page]
                    NoteJsonList = L2FTNote(Image, Layout, 'Note', NoteItem)
                    for NoteJson in NoteJsonList:
                        PageLayout['Text'].append(NoteJson)
                if not FigureNote[page] == []:
                    FigureNoteItem = FigureNote[page]
                    FigureNoteJsonList = L2FTNote(Image, Layout, 'FigureNote', FigureNoteItem)
                    for FigureNoteJson in FigureNoteJsonList:
                        PageLayout['Text'].append(FigureNoteJson)
                if not TableNote[page] == []:
                    TableNoteItem = TableNote[page]
                    TableNoteJsonList = L2FTNote(Image, Layout, 'TableNote', TableNoteItem)
                    for TableNoteJson in TableNoteJsonList:
                        PageLayout['Text'].append(TableNoteJson)

        if 'Figure' in PageLayout.keys():
            if not Figure[page] == []:
                FigureItem = Figure[page]
                FigureJsonList = Fig2Json(Image, Layout, FigureItem)
                for FigureJson in FigureJsonList:
                    PageLayout['Figure'].append(FigureJson)

        LTPage['PageLayout'].append(PageLayout)
        JsonDict['Pages'].append(LTPage)

    return JsonDict

def L1TexT(PageImage, PageLayout, LTType, L1Text):
    BBoxesList = NoteBBoxes(PageImage, PageLayout, L1Text)
    TextBlock = []

    for index in range(len(L1Text)):
        L1TextBlock = L1Text[index]
        Text = {}

        Text['SemanticType'] = LTType
        Text['location'] = BBoxesList[index][0]
        Text['content'] = L1TextBlock.get_text().replace("\n", " ").replace("- ", "")[:-1]

        Text['TextLines'] = []
        for LineIndex in range(len(L1TextBlock)):
            L1TextLine = L1TextBlock._objs[LineIndex]
            TextLine = {}
            TextLine['content'] = L1TextLine.get_text().replace("-\n", "").replace("\n", "")
            TextLine['location'] = BBoxesList[index][LineIndex+1]
            Text['TextLines'].append(TextLine)

        TextBlock.append(Text)

    return TextBlock

def L2Text(PageImage, PageLayout, LTType, item):
    BBoxesList = getBBoxes(PageImage, PageLayout, item)

    Text = {}

    Text['SemanticType'] = LTType
    Text['content'] = item.get_text().replace("\n", " ").replace("- ", "")[:-1]
    Text['location'] = BBoxesList[0]
    Text['TextLines'] = []

    for index in range(len(item._objs)):
        line = item._objs[index]
        TextLine = {}
        TextLine['content'] = line.get_text().replace("-\n", "").replace("\n", "")
        TextLine['location'] = [BBoxesList[index+1]]
        Text['TextLines'].append(TextLine)

    return Text

def L2Page(PageImage, PageLayout, LTType, item):
    BBoxesList = getBBoxes(PageImage, PageLayout, item)

    Text = {}

    Text['SemanticType'] = LTType
    Text['content'] = ''
    Text['location'] = BBoxesList[0]
    Text['TextLines'] = []

    if isinstance(item, LTFigure):
        for char in item:
            Text['content'] += char._text
    else:
        Text['content'] = item.get_text().replace("\n", " ")[:-1]

    for index in range(len(item._objs)):
        line = item._objs[index]
        TextLine = {}
        TextLine['content'] = line.get_text()
        TextLine['location'] = [BBoxesList[index+1]]
        Text['TextLines'].append(TextLine)

    return Text

def L2FTNote(PageImage, PageLayout, LTType, FTNotes):
    BBoxesList = NoteBBoxes(PageImage, PageLayout, FTNotes)
    TextBlock = []

    for index in range(len(FTNotes)):
        FTNote = FTNotes[index]
        Text = {}
        Text['SemanticType'] = LTType
        content = ''
        for FTNoteLine in FTNote:
            text = FTNoteLine.get_text().replace("\n", "")
            if text[-1] == '-':
                content += text[:-1]
            else:
                content += text + ' '
        Text['content'] = content[:-1]
        Text['location'] = BBoxesList[index][0]
        Text['TextLines'] = []
        for LineIndex in range(len(FTNote)):
            FTNoteLine = FTNote[LineIndex]
            TextLine = {}
            TextLine['content'] = FTNoteLine.get_text()[:-1]
            TextLine['location'] = BBoxesList[index][LineIndex+1]
            Text['TextLines'].append(TextLine)

        TextBlock.append(Text)

    return TextBlock

def Fig2Json(PageImage, PageLayout, Figure):
    FigureJsonList = []

    for fig in Figure:
        Text = {}
        location = coordinateChange(PageImage, PageLayout, fig)
        Text["location"] = location
        FigureJsonList.append(Text)

    return FigureJsonList