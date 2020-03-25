
from utils.formatChange.coordinateChange import *

def rst2json(conf, fileName, semseg, PagesLayout):
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
    Column_Header = None
    Row_Header = None
    Body = None

    JsonDict = {}
    JsonDict['FileName'] = fileName
    JsonDict['Pages'] = []

    if TIT == 0 or TIT == 1:
        if TextLevel == 1:
            L1Text = semseg.Text.Text
        else:
            Text = semseg.Text.Text
            Title = semseg.Text.Title
            Author = semseg.Text.Author
            Page = semseg.Text.Page
            Note = semseg.Text.Note
            FigureNote = semseg.Text.FigureNote
            TableNote = semseg.Text.TableNote
        if TIT == 0:
            Figure = semseg.Image.Image
            Table = semseg.Table.Table
            Column_Header = semseg.Table.Column_Header
            Row_Header = semseg.Table.Row_Header
            Body = semseg.Table.Body

    elif TIT == 2:
        Figure = semseg.Image.Image
    else:
        Table = semseg.Table.Table
        Column_Header = semseg.Table.Column_Header
        Row_Header = semseg.Table.Row_Header
        Body = semseg.Table.Body

    for page in range(semseg.Page):
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
                    TextJson = L1TexT(Layout, 'L1Text', TextItem)
                    PageLayout['Text'].append(TextJson)
            else:
                if not Title[page] == []:
                    TitleItem = Title[page]
                    TitleJson = L2Text(Layout, 'Title', TitleItem)
                    PageLayout['Text'].append(TitleJson)
                if not Author[page] == []:
                    AuthorItem = [Author[page]]
                    AuthorJson = L2FTNote(Layout, 'Author', AuthorItem)[0]
                    PageLayout['Text'].append(AuthorJson)
                if not Page[page] == []:
                    PageItem = Page[page][0]
                    PageJson = L2Page(Layout, 'PageNo', PageItem)
                    PageLayout['Text'].append(PageJson)
                if not Note[page] == []:
                    NoteItem = Note[page]
                    NoteJsonList = L2FTNote(Layout, 'Note', NoteItem)
                    for NoteJson in NoteJsonList:
                        PageLayout['Text'].append(NoteJson)
                if not FigureNote[page] == []:
                    FigureNoteItem = FigureNote[page]
                    FigureNoteJsonList = L2FTNote(Layout, 'FigureNote', FigureNoteItem)
                    for FigureNoteJson in FigureNoteJsonList:
                        PageLayout['Text'].append(FigureNoteJson)
                if not TableNote[page] == []:
                    TableNoteItem = TableNote[page]
                    TableNoteJsonList = L2FTNote(Layout, 'TableNote', TableNoteItem)
                    for TableNoteJson in TableNoteJsonList:
                        PageLayout['Text'].append(TableNoteJson)
                if not Text[page] == []:
                    TextItem = Text[page]
                    TextJsonList = L2MainText(Layout, 'Text', TextItem)
                    for TextJson in TextJsonList:
                        PageLayout['Text'].append(TextJson)

        if 'Figure' in PageLayout.keys():
            if not Figure[page] == []:
                FigureItem = Figure[page]
                FigureJsonList = Fig2Json(Layout, FigureItem)
                for FigureJson in FigureJsonList:
                    PageLayout['Figure'].append(FigureJson)

        if 'Table' in PageLayout.keys():
            if not Table[page] == []:
                TableItem = Table[page]
                CHeaderItem = Column_Header[page]
                RHeaderItem = Row_Header[page]
                BodyItem = Body[page]

                TableJsonList = Fig2Json(Layout, TableItem)
                CJsonList, RJsonList, BJsonList = CRB2Json(Layout, CHeaderItem, RHeaderItem, BodyItem)

                for index in range(len(TableJsonList)):
                    TableJson = TableJsonList[index]
                    TableJson["row_header"] = RJsonList[index]
                    TableJson["col_header"] = CJsonList[index]
                    TableJson["data"] = BJsonList[index]
                    PageLayout['Table'].append(TableJson)

        LTPage['PageLayout'].append(PageLayout)
        JsonDict['Pages'].append(LTPage)

    return JsonDict

def L1TexT(PageLayout, LTType, L1Text):
    BBoxesList = NoteBBoxes(PageLayout, L1Text)
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

def L2Text(PageLayout, LTType, item):
    BBoxesList = getBBoxes(PageLayout, item)

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

def L2Page(PageLayout, LTType, item):
    BBoxesList = getBBoxes(PageLayout, item)

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

def L2FTNote(PageLayout, LTType, FTNotes):
    BBoxesList = NoteBBoxes(PageLayout, FTNotes)
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

def L2MainText(PageLayout, LTType, MainTexts):
    BBoxesList = NoteBBoxes(PageLayout, MainTexts)
    TextBlock = []

    for index in range(len(MainTexts)):
        MainText = MainTexts[index]
        Text = {}
        Text['SemanticType'] = LTType
        content = ''
        for MainTextLine in MainText:
            text = MainTextLine.get_text().replace("\n", "")
            if text[-1] == '-':
                content += text[:-1]
            else:
                content += text + ' '
        Text['content'] = content[:-1]
        Text['location'] = BBoxesList[index][0]
        Text['TextLines'] = []

        for LineIndex in range(len(MainText._objs)):
            MainTextLine = MainText._objs[LineIndex]
            TextLine = {}
            TextLine['content'] = MainTextLine.get_text()[:-1]
            TextLine['location'] = BBoxesList[index][LineIndex+1]
            Text['TextLines'].append(TextLine)

        TextBlock.append(Text)

    return TextBlock

def Fig2Json(PageLayout, Figure):
    FigureJsonList = []

    for fig in Figure:
        Text = {}
        location = coordinateChange(PageLayout, fig)
        Text["location"] = location
        FigureJsonList.append(Text)

    return FigureJsonList

def CRB2Json(Layout, CHeaderItem, RHeaderItem, BodyItem):
    CHeaderJsonList = []
    RHeaderJsonList = []
    BodyJsonList = []

    for CHeader in CHeaderItem:
        CHeaderJson = []
        for cell in CHeader:
            CellJson = {}
            CellJson["location"] = coordinateChange(Layout, cell[0])
            CellJson["start_row"] = cell[1]
            CellJson["end_row"] = cell[2]
            CellJson["start_col"] = cell[3]
            CellJson["end_col"] = cell[4]
            CellJson["content"] = cell[5]
            CellJson["Children"] = cell[6]
            CHeaderJson.append(CellJson)

        CHeaderJsonList.append(CHeaderJson)
#pdf 2 "content":"SemEval",
    for RHeader in RHeaderItem:
        RHeaderJson = []
        for cell in RHeader:
            CellJson = {}
            CellJson["location"] = coordinateChange(Layout, cell[0])
            CellJson["start_row"] = cell[1]
            CellJson["end_row"] = cell[2]
            CellJson["start_col"] = cell[3]
            CellJson["end_col"] = cell[4]
            CellJson["content"] = cell[5]
            CellJson["Children"] = cell[6]
            RHeaderJson.append(CellJson)

        RHeaderJsonList.append(RHeaderJson)

    for Body in BodyItem:
        BodyJson = []
        for cell in Body:
            CellJson = {}
            CellJson["location"] = coordinateChange(Layout, cell[0])
            CellJson["start_row"] = cell[1]
            CellJson["end_row"] = cell[2]
            CellJson["start_col"] = cell[3]
            CellJson["end_col"] = cell[4]
            CellJson["content"] = cell[5]
            BodyJson.append(CellJson)

        BodyJsonList.append(BodyJson)

    return CHeaderJsonList, RHeaderJsonList, BodyJsonList
