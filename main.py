
from preprocess.pdfminer import layout_analysis
from preprocess.pdf2image import pdf2image
from preprocess.half_full_judge import *

from semseg.text.image_note import FigureNoteExtraction
from semseg.text.table_note import TableNoteExtraction
from semseg.text.author import AuthorExtraction
from semseg.text.title import TitleExtraction
from semseg.text.note import NoteExtraction

from semseg.tools import *
from visualize.annotate import *

from logzero import logger
import numpy as np

import sys
import cv2
import os

if __name__ == '__main__':
    configList = []
    with open('config.txt', 'r') as configFile:
        config = configFile.readlines()
        for index in range(0, len(config), 3):
            cfg = config[index]
            cfgValue = cfg.replace(' ', '').split(":")[1].split('\n')[0]
            configList.append(cfgValue)

    if configList[7] == 'True' or configList[6] == 'True':
        seg_result_folder = 'example/seg_result/'
        if not os.path.exists(seg_result_folder):
            os.mkdir(seg_result_folder)
        if configList[6] == 'True' and not os.path.exists(seg_result_folder + 'image/'):
            os.mkdir(seg_result_folder + 'image/')
        if configList[7] == 'True' and not os.path.exists(seg_result_folder + 'text/'):
            os.mkdir(seg_result_folder + 'text/')

    if configList[2] == 'True':
        fileFolder = configList[0]
    else:
        fileFolder = 'example/pdf_file/'

    if configList[1] == '':
        fileList = sorted(os.listdir(fileFolder))
        fileNum = len(fileList)
    else:
        fileList = [configList[1]]
        fileNum = 1

    for index in range(fileNum):
        fileName = fileList[index]
        if not fileName.endswith('.pdf'):
            logger.info('{} is skipped  ({}/{})'.format(fileName, index+1, fileNum))
            continue
        else:
            logger.info('Processing File {}  ({}/{})'.format(fileName, index+1, fileNum))

        filePath = fileFolder + fileName
        PagesLayout = layout_analysis(filePath)
        PagesImage  = pdf2image(filePath)

        withPageNo = False
        FileFNoteType = []
        FileTNoteType = []
        PageType = half_full_judge(PagesLayout[0])

        for PageNo in range(len(PagesImage)):
            PageImage = PagesImage[PageNo]
            PageLayout = PagesLayout[PageNo]
            PageImage = cv2.cvtColor(np.asarray(PageImage), cv2.COLOR_RGB2BGR)
            Anno_Image = PageImage

            LayoutHeight = PageLayout.height
            liRatio = get_liRatio(PageImage, PageLayout)
            PV = PageVisualize(PageImage, LayoutHeight, liRatio)

            Page, Note = NoteExtraction(PageLayout, PageType)
            if PageNo == 0:
                Title, titleIndex = TitleExtraction(PageLayout)
                PageVisualize.annotate(PV, LTTitle, Title)
                Author = AuthorExtraction(PageLayout, titleIndex)
                PageVisualize.annotate(PV, LTAuthor, Author)
                if not len(Page) == 0:
                    withPageNo = True

            if withPageNo:
                PageVisualize.annotate(PV, LTPageNo, Page)

            PageVisualize.annotate(PV, LTNote, Note)
            Figure, FigNote, FileFNoteType = FigureNoteExtraction(PageLayout, FileFNoteType)
            TabNote, FileTNoteType = TableNoteExtraction(PageLayout, FileTNoteType)
            PageVisualize.annotate(PV, LTFigure, Figure)
            PageVisualize.annotate(PV, LTFigureNote, FigNote)
            PageVisualize.annotate(PV, LTTableNote, TabNote)

            PageVisualize.show(PV)

            # from visualize.originLayout import layoutImage
            # Anno_Image = layoutImage(Anno_Image, PageLayout, liRatio)
            # cv2.imshow('img', Anno_Image)

        if configList[2] == 'True':
            c = str(input())
            if c == 'q':
                sys.exit()

    logger.info("All file processed")