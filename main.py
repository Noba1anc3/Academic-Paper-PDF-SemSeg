
from preprocess.pdfminer import layout_analysis
from preprocess.pdf2image import pdf2image
from preprocess.half_full_judge import *

from extraction.text.image_note import FigureNoteExtraction
from extraction.text.table_note import TableNoteExtraction
from extraction.text.author import AuthorExtraction
from extraction.text.title import TitleExtraction
from extraction.text.note import NoteExtraction

from extraction.tools import *
from visualize.annotate import *

from logzero import logger
import numpy as np
import sys
import cv2
import os

status = 1
#DEBUG状态下读取的是外目录下的pdf文件夹，并且每个文件处理完成后需要在控制台按任意键回车
#按q键则会终止程序执行
#RUN状态下读取的是内目录下'example/pdf_file/'下的文件，所有文件依次顺序处理
#在每一页运行出结束后按任意键跳页即可，不需要中途干预

if __name__ == '__main__':
    if not os.path.exists('example/analysis_result/'):
        os.mkdir('example/analysis_result/')

    if status == 1:
        fileFolder = '../pdf/'
    else:
        fileFolder = 'example/pdf_file/'

    fileList = sorted(os.listdir(fileFolder))
    fileNum = len(fileList)

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

        if status == 1:
            c = str(input())
            if c == 'q':
                sys.exit()

    logger.info("All file processed")