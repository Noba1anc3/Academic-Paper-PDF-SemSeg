
from utils.pdfminer import *
from extraction import *

from logzero import logger

import numpy as np
import sys

status = DEBUG   #DEBUG/RUN
#DEBUG状态下读取的是外目录下的pdf文件夹，并且每个文件处理完成后需要在控制台按任意键回车
#按q键则会终止程序执行
#RUN状态下读取的是内目录下'example/pdf_file/'下的文件，所有文件依次顺序处理
#在每一页运行出结束后按任意键跳页即可，不需要中途干预

if __name__ == '__main__':
    if not os.path.exists('example/analysis_result/'):
        os.mkdir('example/analysis_result/')

    if status == DEBUG:
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
        PagesImage  = pdf_to_image(filePath)
        withPageNo = False
        PageType = half_full_judge(PagesLayout[0])

        for PageNo in range(len(PagesImage)):
            PageImage = PagesImage[PageNo]
            PageLayout = PagesLayout[PageNo]

            PageImage = cv2.cvtColor(np.asarray(PageImage), cv2.COLOR_RGB2BGR)
            Anno_Image = PageImage
            LayoutHeight = PageLayout.height
            liRatio = get_liRatio(PageImage, PageLayout)

            Page, Note = noteExtraction(PageLayout, PageType)

            if PageNo == 0:
                Title, titleIndex, titleError = titleExtraction(PageLayout)
                if titleError:
                    logger.info('Unexpected Error when Locating Title in Page {} of File {}'.format(PageNo, fileName))
                else:
                    BBoxes = getBoundingBoxes(LayoutHeight, Title, liRatio)
                    PageImage = drawBox(PageImage, LTTitle, BBoxes)

                Author = AuthorExtraction(PageLayout, titleIndex)
                BBoxes = getBoundingBoxes(LayoutHeight, Author, liRatio)
                PageImage = drawBox(PageImage, LTAuthor, BBoxes)
                if not len(Page) == 0:
                    withPageNo = True

            if withPageNo:
                PageBBoxes = getBoundingBoxes(LayoutHeight, Page, liRatio)
                PageImage = drawBox(PageImage, LTPageNo, PageBBoxes)
            NoteBBoxes = getBoundingBoxes(LayoutHeight, Note, liRatio)
            PageImage = drawBox(PageImage, LTNote, NoteBBoxes)

            FigNote, TabNote = figTableExtraction(PageLayout)
            FigNoteBBoxes = getBoundingBoxes(LayoutHeight, FigNote, liRatio)
            TabNoteBBoxes = getBoundingBoxes(LayoutHeight, TabNote, liRatio)
            PageImage = drawBox(PageImage, LTFigureNote, FigNoteBBoxes)
            PageImage = drawBox(PageImage, LTTableNote, TabNoteBBoxes)

            height, width = PageImage.shape[:2]
            size = (int(height*0.8), int(width*1.2))
            PageImage = cv2.resize(PageImage, size)
            #Anno_Image = layoutImage(Anno_Image, PageLayout, liRatio)
            cv2.imshow('img', PageImage)
            #cv2.imshow('img', Anno_Image)
            cv2.waitKey(0)

            # if not os.path.exists('example/analysis_result/' + fileName[:-4]):
            #     os.mkdir('example/analysis_result/' +fileName[:-4])
            # cv2.imwrite('example/analysis_result/' + fileName[:-4] + '/' + str(PageNo) + '.jpg', Anno_Image)

        if status == DEBUG:
            c = str(input())
            if c == 'q':
                sys.exit()

    logger.info("All file processed")