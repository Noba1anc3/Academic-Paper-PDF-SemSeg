from pdfminer.layout import *
import sys

sys.dont_write_bytecode = True

def Leve1Extraction(PageLayout):
    Text = []

    for Box in PageLayout:
        if isinstance(Box, LTTextBoxHorizontal):
            Text.append(Box)

    return Text