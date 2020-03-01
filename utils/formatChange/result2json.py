import json
from utils.formatChange.visualize.annotate import PageVisualize

def rst2json(conf, fileName, semseg, PagesImage, PagesLayout):
    TIT = conf.tit_choice
    TextLevel = conf.text_level

    Text = None
    Title = None
    Author = None
    Page = None
    Note = None
    FigureNote = None
    TableNote = None

    Image = None
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
            Image = semseg.Image.Image
    elif TIT == 2:
        Image = semseg.Image.Image
    else:
        pass

    for page in range(semseg.Page):
        PV = PageVisualize(PagesImage[page], PagesLayout[page])
        LTPage = {}
        LTPage['PageNo'] = page + 1
        LTPage['PageLayout'] = []
        PageLayout = {}

        if TIT == 0 or TIT == 1:
            PageLayout['Text'] = []
            if TIT == 0:
                PageLayout['Image'] = []
                PageLayout['Table'] = []
        elif TIT == 2:
            PageLayout['Image'] = []
        else:
            PageLayout['Table'] = []

        if 'Text' in PageLayout.keys():
            Text = {}

            if TextLevel == 1:
                Text['SemanticType'] = 'L1Text'
            else:
                if not Title[page] == []:
                    TitleItem = Title[page][0]
                    Text = L2Text('Title', TitleItem, PV)
                    PageLayout['Text'].append(Text)
                if not Author[page] == []:
                    AuthorItem = Author[page][0]
                    Text = L2Text('Author', AuthorItem, PV)
                    PageLayout['Text'].append(Text)
                if not Page[page] == []:
                    PageItem = Page[page][0]
                    Text = L2Text('Page', PageItem, PV)
                    PageLayout['Text'].append(Text)
                if not Note[page] == []:
                    NoteItem = Note[page][0]
                    Text = L2Text('Note', NoteItem, PV)
                    PageLayout['Text'].append(Text)
                # if not FigureNote[page] == []:
                #     FigureNote = FigureNote[page][0]
                #     Text = L2FTNote('FigureNote', FigureNote)
                #     PageLayout['Text'].append(Text)
                # if not TableNote[page] == []:
                #     TableNote = FigureNote[page][0]
                #     Text = L2FTNote('TableNote', TableNote)
                #     PageLayout['Text'].append(Text)
        if 'Image' in PageLayout.keys():
            pass

        if Text == None:
            pass
        if not Title == None:
            pass

        LTPage['PageLayout'].append(PageLayout)
        JsonDict['Pages'].append(LTPage)

    print(JsonDict)

    return JsonDict

def L2Text(LTType, item, PV):
    PV.coordinateChange()
    XleftUp = int(item.x0 / PV.liRatio[0])
    YleftUp = int((PV.LayoutHeight - item.y1) / PV.liRatio[1])
    XrightDown = int(item.x1 / PV.liRatio[0])
    YrightDown = int((PV.LayoutHeight - item.y0) / PV.liRatio[1])

    Text = {}

    Text['SemanticType'] = LTType
    Text['content'] = item.get_text()
    Text['location'] = [XleftUp, YleftUp, XrightDown, YrightDown]
    Text['TextLines'] = []

    for line in item._objs:
        TextLine = {}
        TextLine['content'] = line.get_text()[:-2]
        TextLine['location'] = [int(line.x0), int(line.y0), int(line.x1), int(line.y1)]
        Text['TextLines'].append(TextLine)

    return Text

# def L2FTNote(LTType, FTNote):
#     Text = {}
#     Text['SemanticType'] = LTType
#
#     for Line in FTNote:
