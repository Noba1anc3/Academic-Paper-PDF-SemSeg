
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
import argparse
import sys
import cv2
import os

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", type=str, default='../pdf/pdf_file/', help="pdf file's folder")
    parser.add_argument("--filename", type=str, default='', help="specify a unique pdf file with '.pdf' ")
    parser.add_argument("--debug", default=True, help="whether debug or not")
    parser.add_argument("--seg_level", type=int, default=1,
                        help="1: level-1 segmentation on text and image, 2: level-2 segmentation on text and image")
    parser.add_argument("--table_level", type=int, default=1,
                        help="1: only segment the bounding box of tables, 2: segment all the cells in the tables, additionally")
    parser.add_argument("--tit_choice", type=int, default=0,
                        help="0: segment all kinds of semantic type, 1: only segment text out, 2: only segment image out, 3: only segment table out")
    parser.add_argument("--save_image", default=True, help="whether save the image result of segmentation")
    parser.add_argument("--save_text", default=True, help="whether save the text result of segmentation")
    opt = parser.parse_args()
    print(opt)

    if opt.save_image == True or opt.save_text == True:
        seg_result_folder = 'example/seg_result/'
        if not os.path.exists(seg_result_folder):
            os.mkdir(seg_result_folder)
        if opt.save_image == True and not os.path.exists(seg_result_folder + 'image/'):
            os.mkdir(seg_result_folder + 'image/')
        if opt.save_text == True and not os.path.exists(seg_result_folder + 'text/'):
            os.mkdir(seg_result_folder + 'text/')

    if opt.debug == True:
        fileFolder = opt.folder
    else:
        fileFolder = 'example/pdf_file/'

    if opt.filename == '':
        fileList = sorted(os.listdir(fileFolder))
        fileNum = len(fileList)
    else:
        fileList = [opt.filename]
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

        if opt.debug == True:
            c = str(input())
            if c == 'q':
                sys.exit()

    logger.info("All file processed")