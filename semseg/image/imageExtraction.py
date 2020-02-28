from semseg.image.image import ImgExtraction

class ImageExtraction():
    def __init__(self, PagesLayout):
        self.Image = []
        self.PagesLayout = PagesLayout
        self.Segmentation()

    def Segmentation(self):
        for PageNo in range(len(self.PagesLayout)):
            PageLayout = self.PagesLayout[PageNo]
            Image = ImgExtraction(PageLayout)
            self.Image.append(Image)