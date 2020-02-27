from semseg.text.textExtraction import TextExtraction
from semseg.image.imageExtraction import ImageExtraction
from semseg.table.tableExtraction import TableExtraction

class SemanticSegmentation():
    def __init__(self, conf, PagesImage, PagesLayout):
        self.Text = []
        self.Image = []
        self.Table = []
        self.configList = conf
        self.PagesImage = PagesImage
        self.PagesLayout = PagesLayout
        self.Segmentation()

    def Segmentation(self):
        TextLevel = self.configList.text_level
        TableLevel = self.configList.table_level

        if not self.configList.tit_choice:
            Text = TextExtraction(TextLevel, self.PagesImage, self.PagesLayout)
            Image = ImageExtraction(self.PagesLayout)
            Table = TableExtraction(TableLevel, self.PagesLayout)

        elif self.configList.tit_choice == 1:
            Text = TextExtraction(TextLevel, self.PagesImage, self.PagesLayout)

        elif self.configList.tit_choice == 2:
            Image = ImageExtraction(self.PagesLayout)

        else:
            Table = TableExtraction(TableLevel, self.PagesLayout)
