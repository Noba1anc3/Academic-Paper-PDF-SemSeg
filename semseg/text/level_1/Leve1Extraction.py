from pdfminer.layout import *

def Leve1Extraction(PageLayout):
    Text = []

    for Box in PageLayout:
        if isinstance(Box, LTTextBoxHorizontal):
            Text.append(Box)

    return Text